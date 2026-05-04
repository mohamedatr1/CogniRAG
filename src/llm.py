import logging
from langchain_core.language_models import BaseChatModel
from config.settings import settings

logger = logging.getLogger(__name__)


def get_llm() -> BaseChatModel:
    """Groq → Ollama → FakeLLM fallback chain."""
    if settings.GROQ_API_KEY:
        try:
            from langchain_groq import ChatGroq
            logger.info("Using Groq: %s", settings.GROQ_MODEL)
            return ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=settings.GROQ_MODEL,
                temperature=0.1,
            )
        except Exception as e:
            logger.warning("Groq init failed: %s", e)

    # try:
        # from langchain_ollama import ChatOllama
        # logger.info("Falling back to Ollama llama3")
        # return ChatOllama(model="llama3", base_url=settings.OLLAMA_BASE_URL)
    # except Exception as e:
        # logger.warning("Ollama init failed: %s", e)

    from langchain_core.language_models.fake import FakeListChatModel
    logger.warning("Using mock LLM — set GROQ_API_KEY in .env")
    return FakeListChatModel(
        responses=["⚠️ No LLM configured. Add GROQ_API_KEY to your .env file."]
    )