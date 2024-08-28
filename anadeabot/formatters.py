from collections.abc import Iterable

from langchain_core.documents import Document

from anadeabot.schemas import DesignChoice


def format_design(design: DesignChoice) -> str:
    formatted = []
    for attribute, choice in design:
        formatted.append(f'{attribute}: {str(choice)}')
    return '\n'.join(formatted)


def format_faq(documents: Iterable[Document]) -> str:
    faq = []
    for i, d in enumerate(documents):
        question = d.page_content
        answer = d.metadata['answer']
        faq.append(f'{i + 1}. Question: {question} Answer: {answer}')
    return '\n'.join(faq)


def format_grounding(documents: Iterable[Document]) -> str:
    formatted = []
    for i, document in enumerate(documents):
        formatted.append(f'{i + 1}. {document.page_content}')
    return '\n'.join(formatted)
