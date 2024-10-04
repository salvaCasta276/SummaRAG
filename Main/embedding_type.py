from enum import Enum
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings


class EmbeddingType(Enum):
    HuggingFace = 384,
    OpenAI = 1536

    def __init__(self, embedding_size):
        self.embedding_size = embedding_size

    def get_embedding(self, uses_gpu=False):
        model_kwargs = {}
        if uses_gpu:
            model_kwargs["device"] = "cuda"

        if self == EmbeddingType.HuggingFace:
            return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs=model_kwargs)
        elif self == EmbeddingType.OpenAI:
            return OpenAIEmbeddings(model_kwargs=model_kwargs, model_name="gpt-3.5-turbo")
