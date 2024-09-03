from langchain_core.messages import HumanMessage
from langchain_openai.chat_models import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from anadeabot import prompts
from anadeabot.settings import settings
from anadeabot.graph import create_graph, ConfigSchema

from evaluation.dataset import State, Dataset, load_dataset


class Evaluator:
    def __init__(self):
        self.llm = ChatOpenAI(model=settings.model, api_key=settings.OPENAI_API_KEY, temperature=0.1)

    def setup(self):
        config = ConfigSchema(llm=self.llm, thread_id='_')
        agent = create_graph(MemorySaver()).with_config({'configurable': config})
        agent.invoke({'messages': [prompts.start_agent_system_prompt, prompts.greeting_prompt]})
        return agent

    def run(self, dataset: Dataset) -> tuple[list[list], list[list]]:
        y_true = []
        y_pred = []

        for conversation in dataset.conversations:
            agent = self.setup()

            expected_states = []
            predicted_states = []

            for turn in conversation.turns:
                state = agent.invoke({'messages': HumanMessage(turn.user_message)})
                if turn.expected_state:
                    expected_states.append(turn.expected_state)
                    predicted_states.append(State(**state))

            y_true.append(expected_states)
            y_pred.append(predicted_states)

        return y_true, y_pred


def evaluate():
    dataset = load_dataset('evaluation/datasets/choice_detection.yaml')
    evaluator = Evaluator()
    y_true, y_pred = evaluator.run(dataset)
    print([s.design for s in y_true[0]])
    print([s.design for s in y_pred[0]])
