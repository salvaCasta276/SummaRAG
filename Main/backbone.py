import openai
import langchain
import os
import pinecone
from enum import Enum
from langchain_community.document_loaders import PyPDFDirectoryLoader, TextLoader, DirectoryLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

class DocumentLoader:
    def __init__(self, path):
        # Reads custom data from local file
        self.loader = JSONLoader(
            file_path=path,
            jq_schema='{ "page_content": .content, "url": .url, "title": .title, "author": .author, "date": .date }',
            content_key='.page_content',
            is_content_key_jq_parsable=True,
            metadata_func=self.extract_metadata,
            text_content=False)
        
    def extract_metadata(self, json_dict, metadata):
        return {
            "url": json_dict.get("url"),
            "title": json_dict.get("title"),
            "author": json_dict.get("author"),
            "date": json_dict.get("date")
        }

    def load(self):
        return self.loader.load()  # Load the document from the path
    
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

        self.vectorstore = PineconeVectorStore(index_name=index_name, embedding=embedding) # initializes a PineconeVectorStore object using the index_name and the provided embeddings model or function
        return self.vectorstore


if __name__ == "__main__":
    files = os.listdir("ainewscraper/output/")
    docs_loader = []

    for file in files:
        docs_loader.append(DocumentLoader(path="ainewscraper/output/" + file))

    splitter = TextSplitter()
    chunks = splitter.get_chunks(docs_loader[0].load())

    embedding = EmbeddingType.get_embedding(EmbeddingType.HuggingFace, "sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = VectorStore(index_name="ainews", embedding=embedding)
