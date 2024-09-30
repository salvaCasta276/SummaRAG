import os
import yaml

from enum import Enum
from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain_community.llms import HuggingFaceHub

from dotenv import load_dotenv

from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

import cleaning

with open('config.yaml') as f:
    config = yaml.safe_load(f)


class DocumentLoader:
    def __init__(self, path):
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
        return self.loader.load()

class TextSplitter:
    def __init__(self, chunk_size=config['chunk_size'], chunk_overlap=config['chunk_overlap']):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True)

    def get_chunks(self, docs):
        return self.text_splitter.split_documents(docs)

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
            return OpenAIEmbeddings(model_name='gpt', model_kwargs=model_kwargs)

class VectorStore:
    def __init__(self, index_name, embedding_type):
        pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])

        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name,
                dimension=embedding_type.embedding_size,
                metric=config['metric'],
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )

        self.database = PineconeVectorStore(index_name=index_name, embedding=embedding_type.get_embedding())

def clean_text(text):
    return cleaning.clean_content(text)

if __name__ == "__main__":
    load_dotenv()

    files = os.listdir("ainewscraper/output")
    docs_loader = []


    for file in files:
        docs_loader.append(DocumentLoader(path="ainewscraper/output" + file))

    splitter = TextSplitter()

    embedding_type = EmbeddingType.HuggingFace
    vectorstore = VectorStore(index_name="ainews", embedding_type=embedding_type)

    all_chunks = []
    for loader in docs_loader:
        docs = loader.load()
        
        # Clean the text
        for doc in docs:
            doc.page_content = clean_text(doc.page_content)
        
        chunks = splitter.get_chunks(docs)
        all_chunks.extend(chunks)

    #print('First chunk', all_chunks[0])
    #vectorstore.database.similarity_search()
    # Save all chunks to Pinecone
    vectorstore.database.add_documents(all_chunks)
    print("All documents have been saved to Pinecone.")
