import os
from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Iterable, Self, TypeAlias

from src.main.consts import DATA_DIR


class ModelName(Enum):
    """
    Models to choose from.
    Variants:
    - openai/gpt-4o
    - openai/gpt-4o-mini
    - openai/o1-mini
    - anthropic/claude-3-sonnet
    - anthropic/claude-3-haiku
    """

    gpt_4o = "openai/gpt-4o"
    gpt_4o_mini = "openai/gpt-4o-mini"
    o1_mini = "openai/o1-mini"
    claude_3_sonnet = "anthropic/claude-3-sonnet"
    claude_3_haiku = "anthropic/claude-3-haiku"


@dataclass
class GenerationSettings:
    """
    Settings for generation.
    Parameters:
    - model - model to use
    - temperature - temperature for generation
    - n - number of generations
    - max_tokens - max tokens for generation
    - frequency_penalty - frequency penalty for generation. Penalizes repetition.
    - presence_penalty - presence penalty for generation. Penalizes new tokens.
    """

    model: ModelName
    temperature: float = 1.0
    n: int = 1
    max_tokens: int = 3000
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        result = {field.name: getattr(self, field.name) for field in fields(self)}
        result["model"] = result["model"].value
        return result


class Role(Enum):
    """
    Role of the message.
    Variants:
    - system
    - user
    - assistant
    """

    system = "system"
    user = "user"
    assistant = "assistant"


@dataclass
class Message:
    """
    Message in chat.
    Parameters:
    - role - role of the message
    - content - content of the message
    """

    role: Role
    content: str

    def to_dict(self) -> dict:
        """
        Convert message to dict. So you can use it in OpenAI API.
        """
        return {
            "role": self.role.value,
            "content": self.content,
        }

    def __str__(self) -> str:
        return f"## {self.role}: \n{self.content}"


DocumentName: TypeAlias = str


@dataclass
class Document:
    """
    Document to save.
    Parameters:
    - name - name of the document
    - content - content of the document
    - filename - filename of the document
    """

    name: DocumentName
    content: str
    filename: str | None = None

    def __post_init__(self):
        if self.filename is None:
            return
        path = DATA_DIR / self.filename
        os.makedirs(path.parent, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            f.write(self.content)

    def __str__(self) -> str:
        return f"# {self.name}: \n{self.content}"


class DocumentsStore:
    """
    Store of documents.
    """

    def __init__(self, documents: dict[DocumentName, Document] | None = None):
        self.documents: dict[DocumentName, Document] = documents or {}

    def update(self, documents: Self | dict[DocumentName, Document]) -> Self:
        if isinstance(documents, dict):
            self.documents.update(documents)
        else:
            self.documents.update(documents.documents)
        return self

    def add(self, document: Document) -> None:
        self.documents[document.name] = document

    def get_documents(self, document_names: list[DocumentName]) -> list[Document]:
        return [self.documents[name] for name in document_names]

    def contains(self, document_names: Iterable[DocumentName]) -> bool:
        document_names = set(document_names)
        return document_names.issubset(set(self.documents.keys()))
