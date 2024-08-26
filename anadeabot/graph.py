from typing import TypedDict, Annotated

from langchain_core.messages import SystemMessage, AnyMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.state import CompiledStateGraph

from anadeabot.tools import option_tools
from anadeabot.schemas import DesignChoice, BooleanOutput, UserIntent, format_design
from anadeabot.helpers import missing_attributes
from anadeabot.prompts import (
    choice_detection_prompt,
    ask_for_confirmation_prompt,
    ask_missing_attribute_prompt,
    design_satisfaction_prompt,
    user_is_not_satisfied_prompt,
    check_for_confirmation_prompt,
    acknowledge_order_prompt,
)

TOOLS = [*option_tools]


def design_reducer(old, new):
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
    llm = config['configurable']['llm']
    structured = llm.with_structured_output(UserIntent)
    intent = structured.invoke(state['messages'])
    detected = [i for i, detected in intent if detected]
    return detected[0] if detected else 'agent'


def decision_node(state: State, config: RunnableConfig):
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


def confirm_node(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    structured = llm.with_structured_output(BooleanOutput)
    chain = (check_for_confirmation_prompt | structured)
    confirmation = chain.invoke(state['messages'])
    response = (acknowledge_order_prompt | llm).invoke(state['messages'])
    return {'confirmed': confirmation.value, 'messages': response}


def question_node(state: State, config: RunnableConfig):
    return state


def agent(state: State, config: RunnableConfig):
    llm = config['configurable']['llm']
    llm_with_tools = llm.bind_tools(TOOLS)
    return {'messages': llm_with_tools.invoke(state['messages'])}


def create_graph(checkpointer) -> CompiledStateGraph:
    graph_builder = StateGraph(State, config_schema=ConfigSchema)
    graph_builder.add_node('agent', agent)
    graph_builder.add_node('choice', choice_node)
    graph_builder.add_node('confirm', confirm_node)
    graph_builder.add_node('decision', decision_node)
    graph_builder.add_node('question', question_node)
    graph_builder.add_node('tools', ToolNode(TOOLS))
    graph_builder.add_edge(START, 'choice')
    graph_builder.add_conditional_edges('choice', intent_node, ['decision', 'question', 'confirm', 'agent'])
    graph_builder.add_edge('decision', 'agent')
    graph_builder.add_edge('question', 'agent')
    graph_builder.add_edge('tools', 'agent')
    graph_builder.add_conditional_edges('agent', tools_condition)
    graph_builder.add_edge('confirm', END)
    graph = graph_builder.compile(checkpointer=checkpointer)
    return graph
