from config.settings import settings


def get_embeddings():
    if settings.EMBEDDING_MODEL == "openai" and settings.OPENAI_API_KEY:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model="text-embedding-3-small")
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name=settings.HUGGINGFACE_EMBEDDING_MODEL)