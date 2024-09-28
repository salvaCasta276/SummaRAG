# -*- coding: utf-8 -*-
"""Langchain - Pinecone.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EhDlD33mz1_ltKVyig9SuDLbBi0TDH28

# PINECONE

# Load Dependencies 👩‍💻👨‍💻

Antes de ejecutar:
- Cargar una carpeta docs/ con archivos .txt que serán la knowledge base
- Usar T4 en el ambiente o modificar 'cuda' a 'gpu'
- Cargar un archivo .env con las API KEYS de HuggingFace/OpenAI y Pinecone
"""



import openai
import langchain
import os
from langchain.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
import logging

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] - %(message)s ',
                    handlers=[
                        logging.FileHandler('/content/langchaindemo.log', mode='w'),
                        logging.StreamHandler(),
                    ],
                    force=True)
logger = logging.getLogger(__name__)
logger.info("Langchain Demo Initialized")

"""# Document Loader 📑📚

Load data from a source as Document's. A Document is a piece of text and associated metadata.

https://api.python.langchain.com/en/latest/document_loaders/langchain_community.document_loaders.directory.DirectoryLoader.html
"""

def get_docs():
    """
    Loads each file into one document (knowledge base)
    :return: docs
    """

    loader = DirectoryLoader(  # Reads custom data from local files
        path="docs",
        glob="*.txt",
        loader_cls=TextLoader  # Loader class to use for loading files
    )

    docs = loader.load()
    return docs

docs = get_docs()
docs[0]

"""# Text Splitters 📖✂️

Split a long document into smaller chunks that can fit into your model's context window

https://js.langchain.com/v0.1/docs/modules/data_connection/document_transformers/

Los separadores pueden ser pasados como argumento y se puede usar la funcion 'create_documents' si no utilizamos un DocumentLoader
"""

def get_chunks(docs, chunk_size=1000, chunk_overlap=200):
    """
    Get chunks from docs. Our loaded doc may be too long for most models, and even if it fits it can struggle to find relevant context. So we generate chunks
    :param docs: docs to be splitted

    :return: chunks
    """

    text_splitter = RecursiveCharacterTextSplitter( # recommended splitter for generic text. split documents recursively by different characters - starting with "\n\n", then "\n", then " "
        chunk_size=chunk_size,        # max size (in terms of number of characters) of the final documents
        chunk_overlap=chunk_overlap,  # how much overlap there should be between chunks
        add_start_index=True
    )
    chunks = text_splitter.split_documents(docs)
    logger.info(f"Split {len(docs)} documents into {len(chunks)} chunks.")
    return chunks

chunks = get_chunks(docs)
chunks

"""### Note: Start_index metadata 📝
 When you need to reassemble the chunks into the original document format, start_index helps in placing each chunk at the correct position.

 Determine where in the original document each chunk belongs.

# Embeddings 🤔
"""

from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings( #  embedding=OpenAIEmbeddings() rate limit
        model_name='sentence-transformers/all-MiniLM-L6-v2',
        model_kwargs={'device': 'cuda'} #TODO CHANGE IF NOT USING GPU
)

vector = embeddings.embed_query("Hola como estas?")
embedding_size = len(vector)  # HF 384 ; OPENAI 1536
embedding_size

vector

"""Para la próxima clase:

❓ Por que es mejor/peor la longitud del embedding vector?

❓ Qué algoritmo de embedding usa HF embeddings?

# Vector Store 🗃️
"""

import pinecone
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore

def get_vector_store(index_name, embeddings, embedding_size=384):
  """ Creates vector store from Pinecone for storing and managing embeddings.

    :param str index_name: The name of the index to create or retrieve from Pinecone.
    :param str embeddings: The embedding function to be used to generate embeddings
    :param int embedding_size: The size (dimension) of the embeddings. Defaults to 384 (e.g., for sentence-transformers/all-MiniLM-L6-v2).

    :return: PineconeVectorStore: An object representing the vector store in Pinecone for managing embeddings.

    :raise: ValueError: If the index creation fails due to invalid parameters or connection issues.
  """

  pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])  # Pinecone is initialized using an API key stored in the environment variable

  if INDEX_NAME not in pc.list_indexes().names():        # Check whether an index with the given index_name already exists
      pc.create_index(
          name=INDEX_NAME,          # Name of the index
          dimension=embedding_size, # Size of the vectors (embeddings)
          metric="cosine",          # Distance metric used to compare vectors
          spec=ServerlessSpec(      # Determines the infrastructure used
              cloud='aws',          # Specifies that the Pinecone index is hosted on AWS
              region='us-east-1'    # Specifies the region of the cloud provider
          )
      )

  vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings) # initializes a PineconeVectorStore object using the index_name and the provided embeddings model or function

  return vectorstore

"""❗❗❗❗ VAMOS A PINECONE -> https://app.pinecone.io/"""

INDEX_NAME = "langchain-demo-index-dl"
vectorstore = get_vector_store(INDEX_NAME, embeddings, embedding_size)

vectorstore.add_documents(chunks)

"""### Similarity Search 📝


- similarity: It retrieves the documents that are most similar to the query based on their embeddings, cos similarity

- MMR: Maximal Marginal Relevance balances the relevance of documents with the diversity of the results. It ensures that the returned documents are not only similar to the query but also diverse from each other

- Similarity Score Threshold: only those with a score above the threshold are included in the results.


"""

query = "Cuál es temario de la materia Deep Learning?"
vectorstore.search(
    query=query,              # Return docs most similar to query using specified search type.
    search_type="similarity_score_threshold", # can be “similarity”, “mmr”, or “similarity_score_threshold”.
    k=5                       # return top k,
)