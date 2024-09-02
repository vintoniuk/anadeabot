from typing import TypedDict, Annotated
from operator import itemgetter

from langchain_core.messages import SystemMessage, AnyMessage, HumanMessage
from langchain_core.runnables import RunnableConfig, RunnablePassthrough
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.pydantic_v1 import ValidationError

from sqlalchemy.orm import Session

from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode
from langgraph.graph.state import CompiledStateGraph

from anadeabot.tools import option_tools
from anadeabot.formatters import format_design, format_faq, format_grounding
from anadeabot.database import faq_vectorstore, grounding_vectorstore
from anadeabot.helpers import missing_attributes
from anadeabot import database
from anadeabot.schemas import (
    DesignChoice,
    BooleanOutput,
    UserIntent,
    SupportRequest,
)
from anadeabot.prompts import (
    choice_detection_prompt,
    intent_detection_prompt,
    struggle_support_prompt,
    support_details_prompt,
    ask_for_confirmation_prompt,
    ask_missing_attribute_prompt,
    design_satisfaction_prompt,
    user_is_not_satisfied_prompt,
    check_for_confirmation_prompt,
    acknowledge_order_prompt,
    cancel_design_prompt,
    question_refinement_prompt,
    question_faq_prompt,
    format_response_prompt,
    acknowledge_request_prompt,
    check_for_request_details,
    clarify_details_prompt
)

TOOLS = [*option_tools]


def design_reducer(old, new):
    if new is None:
        return DesignChoice()
    update = {}
    for attribute, value in new:
        if value is not None:
            update[attribute] = getattr(new, attribute)
        else:
            update[attribute] = getattr(old, attribute)
    return DesignChoice(**update)


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    design: Annotated[DesignChoice, design_reducer]
    facts: list[Document]


class ConfigSchema(TypedDict):
    llm: BaseChatModel
    thread_id: str
    session: Session


def tool_redirect(destination: str = '__end__', tool_node: str = 'tools'):
    def tool_condition(state):
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get('messages', []):
            ai_message = messages[-1]
        else:
            raise ValueError(f'No messages found in input state to tool_edge: {state}')
        if hasattr(ai_message, 'tool_calls') and len(ai_message.tool_calls) > 0:
            return tool_node
        return destination

    return tool_condition


def grounding_node(state: State):
    if not isinstance(state['messages'][-1], HumanMessage):
        return {'facts': None}
    retriever = grounding_vectorstore.as_retriever(search_kwargs={'k': 5})
    documents = retriever.invoke(state['messages'][-1].content)
    return {'facts': documents}


def intent_node(state: State, config: RunnableConfig):
    if not isinstance(state['messages'][-1], HumanMessage):
        return 'agent'
    llm = config['configurable']['llm']
    structured = llm.with_structured_output(UserIntent)
    chain = (intent_detection_prompt | structured)
    intent = chain.invoke({
        'history': state['messages'],
        'grounding': format_grounding(state['facts'])
    })
    detected = [i for i, detected in intent if detected]
    return detected[0] if detected else 'agent'


def struggle_node(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    chain = (struggle_support_prompt | llm)
    response = chain.invoke({'history': state['messages']})
    return {'messages': response}


def choice_node(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    structured = llm.with_structured_output(DesignChoice)
    chain = (choice_detection_prompt | structured)
    try:
        design = chain.invoke({'history': state['messages']})
    except ValidationError:
        return {'design': DesignChoice()}
    return {'design': design}


def preference_node(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    structured = llm.with_structured_output(BooleanOutput)
    chain = (design_satisfaction_prompt | structured)
    user_is_satisfied = chain.invoke(state['messages'])
    design = format_design(state['design'])
    if missing_attributes(state['design']):
        attribute = missing_attributes(state['design'])[0].upper()
        prompt = ask_missing_attribute_prompt.format(design=design, attribute=attribute)
    elif not user_is_satisfied:
        prompt = user_is_not_satisfied_prompt.format(design=design)
    else:
        prompt = ask_for_confirmation_prompt.format(design=design)
    return {'messages': SystemMessage(prompt)}


def decision_node(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    structured = llm.with_structured_output(BooleanOutput)
    chain = (check_for_confirmation_prompt | structured)
    confirmation = chain.invoke(state['messages'])
    if confirmation.value:
        session = config['configurable']['session']
        user = database.get_user(config['configurable']['thread_id'], session=session)
        database.place_order(user, state['design'], session=session)
        response = (acknowledge_order_prompt | llm).invoke(state['messages'])
    else:
        response = (cancel_design_prompt | llm).invoke(state['messages'])
    return {'messages': response, 'design': None}


def question_node(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    retriever = faq_vectorstore.as_retriever(search_kwargs={'k': 4})
    chain = (
            RunnablePassthrough
            .assign(question=question_refinement_prompt | llm | StrOutputParser())
            .assign(faq=itemgetter('question') | retriever | format_faq)
            | question_faq_prompt | llm)
    return {'messages': chain.invoke({
        'history': state['messages'], 'facts': format_grounding(state['facts'])
    })}


def support_node(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    structured = llm.with_structured_output(BooleanOutput)
    chain = (check_for_request_details | structured)
    has_details = chain.invoke({'history': state['messages']})
    if has_details.value:
        structured = llm.with_structured_output(SupportRequest)
        chain = (support_details_prompt | structured)
        request = chain.invoke({'history': state['messages']})
        session = config['configurable']['session']
        user = database.get_user(config['configurable']['thread_id'], session=session)
        database.make_request(user, request.details, session=session)
        return {'messages': acknowledge_request_prompt}
    else:
        return {'messages': clarify_details_prompt}


def format_node(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    chain = (format_response_prompt | llm)
    last_message = state['messages'].pop()
    response = chain.invoke({'message': last_message.content})
    return {'messages': response}


def agent(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    llm_with_tools = llm.bind_tools(TOOLS)
    return {'messages': llm_with_tools.invoke(state['messages'])}


def create_graph(checkpointer) -> CompiledStateGraph:
    graph_builder = StateGraph(State, config_schema=ConfigSchema)
    graph_builder.add_node('agent', agent)
    graph_builder.add_node('grounding', grounding_node)
    graph_builder.add_node('struggle', struggle_node)
    graph_builder.add_node('decision', decision_node)
    graph_builder.add_node('choice', choice_node)
    graph_builder.add_node('preference', preference_node)
    graph_builder.add_node('question', question_node)
    graph_builder.add_node('tools', ToolNode(TOOLS))
    graph_builder.add_node('format', format_node)
    graph_builder.add_node('support', support_node)
    graph_builder.add_edge(START, 'choice')
    graph_builder.add_edge('choice', 'grounding')
    graph_builder.add_conditional_edges('grounding', intent_node,
                                        ['preference', 'decision', 'question', 'struggle', 'support', 'agent'])
    graph_builder.add_edge('support', 'agent')
    graph_builder.add_edge('struggle', END)
    graph_builder.add_edge('preference', 'agent')
    graph_builder.add_edge('question', 'format')
    graph_builder.add_edge('tools', 'agent')
    graph_builder.add_conditional_edges('agent', tool_redirect('format'), ['tools', 'format'])
    graph_builder.add_edge('decision', END)
    graph_builder.add_edge('format', END)
    graph = graph_builder.compile(checkpointer=checkpointer)
    return graph
