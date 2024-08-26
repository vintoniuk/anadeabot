from typing import TypedDict, Annotated
from operator import itemgetter

from langchain_core.messages import SystemMessage, AnyMessage, HumanMessage
from langchain_core.runnables import RunnableConfig, RunnablePassthrough
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.state import CompiledStateGraph

from anadeabot.tools import option_tools
from anadeabot.schemas import DesignChoice, BooleanOutput, UserIntent
from anadeabot.formatters import format_design, format_faq
from anadeabot.helpers import missing_attributes
from anadeabot.database import vectorstore
from anadeabot.prompts import (
    choice_detection_prompt,
    ask_for_confirmation_prompt,
    ask_missing_attribute_prompt,
    design_satisfaction_prompt,
    user_is_not_satisfied_prompt,
    check_for_confirmation_prompt,
    acknowledge_order_prompt,
    cancel_order_prompt,
    question_refinement_prompt,
    question_faq_prompt
)

TOOLS = [*option_tools]


def design_reducer(old, new):
    update = {}
    if new is None:
        return DesignChoice()
    for attribute, value in new:
        if value is not None:
            update[attribute] = getattr(new, attribute)
        else:
            update[attribute] = getattr(old, attribute)
    return DesignChoice(**update)


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    design: Annotated[DesignChoice, design_reducer]
    confirmed: bool


class ConfigSchema(TypedDict):
    llm: BaseChatModel
    thread_id: str


def choice_node(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    structured = llm.with_structured_output(DesignChoice)
    chain = (choice_detection_prompt | structured)
    design = chain.invoke({'history': state['messages']})
    return {'design': design}


def intent_node(state: State, config: RunnableConfig):
    if not isinstance(state['messages'][-1], HumanMessage):
        return 'agent'
    llm = config['configurable']['llm']
    structured = llm.with_structured_output(UserIntent)
    intent = structured.invoke(state['messages'])
    detected = [i for i, detected in intent if detected]
    return detected[0] if detected else 'agent'


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
        response = (acknowledge_order_prompt | llm).invoke(state['messages'])
        update = {'design': state['design'], 'confirmed': True}
    else:
        response = (cancel_order_prompt | llm).invoke(state['messages'])
        update = {'design': None, 'confirmed': False}
    return {'messages': response} | update


def question_node(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    retriever = vectorstore.as_retriever(search_kwargs={'k': 4})
    chain = (
            RunnablePassthrough
            .assign(question=question_refinement_prompt | llm | StrOutputParser())
            .assign(faq=itemgetter('question') | retriever | format_faq)
            | question_faq_prompt | llm)
    return {'messages': chain.invoke({'history': state['messages']})}


def agent(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    llm_with_tools = llm.bind_tools(TOOLS)
    return {'messages': llm_with_tools.invoke(state['messages'])}


def create_graph(checkpointer) -> CompiledStateGraph:
    graph_builder = StateGraph(State, config_schema=ConfigSchema)
    graph_builder.add_node('agent', agent)
    graph_builder.add_node('choice', choice_node)
    graph_builder.add_node('decision', decision_node)
    graph_builder.add_node('preference', preference_node)
    graph_builder.add_node('question', question_node)
    graph_builder.add_node('tools', ToolNode(TOOLS))
    graph_builder.add_edge(START, 'choice')
    graph_builder.add_conditional_edges('choice', intent_node, ['preference', 'question', 'decision', 'agent'])
    graph_builder.add_edge('preference', 'agent')
    graph_builder.add_edge('question', END)
    graph_builder.add_edge('tools', 'agent')
    graph_builder.add_conditional_edges('agent', tools_condition)
    graph_builder.add_edge('decision', END)
    graph = graph_builder.compile(checkpointer=checkpointer)
    return graph
