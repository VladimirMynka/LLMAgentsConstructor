import os

from openai import AsyncOpenAI

from src.core.agents.agent_parameters import (
    AIAgentParameters,
    ChatAgentParameters,
    CriticAgentParameters,
    HardCodeAgentParameters,
    SimpliestUserMessageRequest,
)
from src.core.agents.agent_typings import DocumentsStore, GenerationSettings, ModelName
from src.core.pipeline import Pipeline
from src.core.prompts import english_prompts

documents_store = DocumentsStore()

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_URL"),
)


system_analyst = Pipeline(
    documents_store=documents_store,
    client=client,
    interviewer=ChatAgentParameters(
        logging_info=("Интервьюер начал интервью", "Интервьюер закончил интервью"),
        system_prompt=english_prompts.interviewer,
        settings=GenerationSettings(
            model=ModelName.gpt_4o,
            temperature=1.1,
            max_tokens=4000,
            frequency_penalty=0.2,
            presence_penalty=0.1,
        ),
        request_user_message=SimpliestUserMessageRequest(),
        chat_name="interviewer_chat",
        last_message_name="interviewer_report",
        chat_filename="1_system_analyst/1_interviewer_chat.md",
        last_message_filename="1_system_analyst/2_interviewer_report.md",
        stop_words=["REPORT", "ОТЧЕТ", "ОТЧЕТ", "ИТОГ"],
        input_document_names=[],
        required_documents=[],
        output_document_name=None,
        output_document_filename=None,
    ),
    interviewer_critic=CriticAgentParameters(
        logging_info=(
            "Интервьюер передал текущую версию отчета критику",
            "Интервьюер исправил всё, о чём просил критик",
        ),
        criticized_agent_name="interviewer",
        max_iterations=10,
        system_prompt=english_prompts.critic_for_interviewer,
        settings=GenerationSettings(model=ModelName.gpt_4o),
        input_document_names=["interviewer_report"],
        required_documents=[],
        output_document_name="interviewer_critic_report",
        output_document_filename="1_system_analyst/3_interviewer_critic_report.md",
    ),
    name_replacer=HardCodeAgentParameters(
        hard_code_logic=lambda x: x.replace("assistant", "System Analyst").replace(
            "user", "Customer"
        ),
        logging_info=(None, "Произведена замена имен"),
        input_document_names=["interviewer_chat"],
        required_documents=["interviewer_critic_report"],
        output_document_name="name_replaced_chat",
        output_document_filename="1_system_analyst/4_name_replaced_chat.md",
    ),
    chat_analyzer=AIAgentParameters(
        logging_info=(
            "Аналитик начал поиск потерянной информации на основе записи интервью",
            "Аналитик закончил поиск потерянной информации на основе записи интервью",
        ),
        system_prompt=english_prompts.chat_analyzer,
        settings=GenerationSettings(model=ModelName.claude_3_sonnet),
        input_document_names=["name_replaced_chat"],
        required_documents=[],
        output_document_name="chat_analyzer_report",
        output_document_filename="1_system_analyst/5_chat_analyzer_report.md",
    ),
    report_extractor=AIAgentParameters(
        logging_info=(
            "Экстрактор начал извлечение отчета из диалога",
            "Экстрактор закончил извлечение отчета из диалога",
        ),
        system_prompt=english_prompts.report_extractor,
        settings=GenerationSettings(
            model=ModelName.claude_3_haiku, temperature=0.7, max_tokens=10000
        ),
        input_document_names=["interviewer_report", "chat_analyzer_report"],
        required_documents=[],
        output_document_name="merged_report",
        output_document_filename="1_system_analyst/6_merged_report.md",
    ),
    translator=AIAgentParameters(
        logging_info=(
            "Переводчик начал перевод отчета",
            "Переводчик закончил перевод отчета",
        ),
        system_prompt=english_prompts.translator,
        settings=GenerationSettings(
            model=ModelName.claude_3_sonnet, temperature=1.0, max_tokens=10000
        ),
        input_document_names=["merged_report"],
        required_documents=[],
        output_document_name="translated_report",
        output_document_filename="1_system_analyst/7_translated_report.md",
    ),
    storyteller=AIAgentParameters(
        logging_info=(
            "Аналитик приступил к воспроизведению пользовательских историй",
            "Аналитик закончил воспроизведение пользовательских историй",
        ),
        system_prompt=english_prompts.storyteller,
        settings=GenerationSettings(
            model=ModelName.claude_3_sonnet,
            temperature=1.2,
            max_tokens=20000,
            frequency_penalty=0.2,
            presence_penalty=0.1,
        ),
        input_document_names=["translated_report"],
        required_documents=[],
        output_document_name="testing_stories",
        output_document_filename="1_system_analyst/8_testing_stories.md",
    ),
    use_cases_writer=AIAgentParameters(
        logging_info=(
            "Аналитик начал запись вариантов использования",
            "Аналитик закончил запись вариантов использования",
        ),
        system_prompt=english_prompts.use_case_writer,
        settings=GenerationSettings(
            model=ModelName.o1_mini,
            temperature=0.7,
            max_tokens=20000,
        ),
        input_document_names=["translated_report"],
        required_documents=[],
        output_document_name="use_cases",
        output_document_filename="1_system_analyst/9_use_cases.md",
    ),
    use_cases_critic=CriticAgentParameters(
        criticized_agent_name="use_cases_writer",
        max_iterations=5,
        logging_info=(
            "Аналитик передал текущую версию вариантов использования критику",
            "Аналитик исправил всё, о чём просил критик",
        ),
        system_prompt=english_prompts.critic_for_use_case_writer,
        settings=GenerationSettings(model=ModelName.gpt_4o),
        input_document_names=["translated_report", "testing_stories", "use_cases"],
        required_documents=[],
        output_document_name="use_cases_critic_report",
        output_document_filename="1_system_analyst/10_use_cases_critic_report.md",
    ),
    domain_modeller=AIAgentParameters(
        logging_info=(
            "Аналитик начал организацию модели предметной области",
            "Аналитик закончил организацию модели предметной области",
        ),
        system_prompt=english_prompts.domain_modeller,
        settings=GenerationSettings(model=ModelName.gpt_4o),
        input_document_names=["translated_report", "use_cases"],
        required_documents=["use_cases_critic_report"],
        output_document_name="domain_model",
        output_document_filename="1_system_analyst/11_domain_model.md",
    ),
    domain_model_critic=CriticAgentParameters(
        criticized_agent_name="domain_modeller",
        max_iterations=5,
        logging_info=(
            "Аналитик передал текущую версию модели предметной области критику",
            "Аналитик исправил всё, о чём просил критик",
        ),
        system_prompt=english_prompts.critic_for_domain_modeller,
        settings=GenerationSettings(model=ModelName.gpt_4o),
        input_document_names=[
            "translated_report",
            "testing_stories",
            "use_cases",
            "domain_model",
        ],
        required_documents=[],
        output_document_name="domain_model_critic_report",
        output_document_filename="1_system_analyst/12_domain_model_critic_report.md",
    ),
    
    result_writer=HardCodeAgentParameters(
        hard_code_logic=lambda x: x,
        logging_info=(
            "Работа системного аналитика закончена",
            None,
        ),
        input_document_names=[],
        required_documents=["domain_model_critic_report"],
        output_document_name=None,
        output_document_filename=None,
    ),
)
