import openai
import langchain
import os
from enum import Enum
from langchain.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore

class DocumentLoader:
    def __init__(self, path):
        # Reads custom data from local file
        self.loader = DirectoryLoader(path="docs", glob="*.txt", loader_cls=TextLoader)  # Loader class to use for loading files
        self.path = path

    def load(self):
        return self.loader.load(self.path)  # Load the document from the path
    
class TextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True)

    def get_chunks(self, docs):
        return self.text_splitter.split_documents(docs)

class EmbeddingType(Enum):
    HuggingFace = 1,
    OpenAI = 2

    @classmethod
    def get_embedding(cls, embedding_type, model_name, uses_gpu=False):
        model_kwargs = {}
        if uses_gpu:
            model_kwargs["device"] = "cuda"

        if embedding_type == cls.HuggingFace:
            return HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)
        elif embedding_type == cls.OpenAI:
            return OpenAIEmbeddings(model_name=model_name, model_kwargs=model_kwargs)

    @classmethod
    def embedding_size(cls, embedding_type):
        if embedding_type == cls.HuggingFace:
            return 384
        elif embedding_type == cls.OpenAI:
            return 1536

class VectorStore:
    def __init__(self, index_name, embedding):
        """ Creates vector store from Pinecone for storing and managing embeddings.

        :param str index_name: The name of the index to create or retrieve from Pinecone.
        :param str embeddings: The embedding function to be used to generate embeddings
        :param int embedding_size: The size (dimension) of the embeddings. Defaults to 384 (e.g., for sentence-transformers/all-MiniLM-L6-v2).

        :return: PineconeVectorStore: An object representing the vector store in Pinecone for managing embeddings.

        :raise: ValueError: If the index creation fails due to invalid parameters or connection issues.
        """
        pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])  # Pinecone is initialized using an API key stored in the environment variable

        if index_name not in pc.list_indexes().names():        # Check whether an index with the given index_name already exists
            pc.create_index(
                name=index_name,          # Name of the index
                dimension=embedding.embedding_size, # Size of the vectors (embeddings)
                metric="cosine",          # Distance metric used to compare vectors
                spec=ServerlessSpec(      # Determines the infrastructure used
                    cloud='aws',          # Specifies that the Pinecone index is hosted on AWS
                    region='us-east-1'    # Specifies the region of the cloud provider
                )
            )

        self.vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=embedding) # initializes a PineconeVectorStore object using the index_name and the provided embeddings model or function
