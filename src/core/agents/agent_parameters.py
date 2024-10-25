import asyncio
from dataclasses import dataclass, fields
import os
from typing import Any, Callable, Coroutine

from src.core.agents.agent_typings import DocumentName, GenerationSettings


class SimpliestUserMessageRequest:
    async def __call__(self, message: str) -> str:
        print(message)
        return input('>>> ')
    
class FromFileUserMessageRequest:
    def __init__(self, filename: str):
        self.filename = filename
        self.answer_filename = f'{filename}.answer'

    async def __call__(self, message: str) -> str:
        with open(f'{self.answer_filename}', 'w') as file:
            file.write(message)
        
        while not os.path.exists(self.filename):
            await asyncio.sleep(0.3)
            
        with open(self.filename, 'r') as file:
            return file.read()


@dataclass
class AgentParameters:
    input_document_names: list[DocumentName]
    output_document_name: DocumentName | None
    logging_info: tuple[str | None, str | None]
    output_document_filename: str | None
    required_documents: list[DocumentName]
    
    def to_dict(self) -> dict[str, Any]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


@dataclass
class AIAgentParameters(AgentParameters):
    system_prompt: str
    settings: GenerationSettings


@dataclass
class CriticAgentParameters(AIAgentParameters):
    criticized_agent_name: str
    max_iterations: int


@dataclass
class ChatAgentParameters(AIAgentParameters):
    request_user_message: Callable[[str], Coroutine[Any, Any, str]]
    chat_name: DocumentName
    last_message_name: DocumentName
    chat_filename: DocumentName | None
    last_message_filename: DocumentName | None
    stop_words: list[str] | None


@dataclass
class HardCodeAgentParameters(AgentParameters):
    hard_code_logic: Callable[[str], str]

