import os
import Main.rag as rag
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import HuggingFaceHub
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

import cleaning

load_dotenv()

# Initialize Pinecone
rag.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))

# Clean the json file containing the posts and save the cleaned posts into a new json file
def process_posts(file_path):
    cleaning.process_posts(file_path)


def initialize_vectorstore(posts):
    embeddings = HuggingFaceEmbeddings()
    texts = clean_and_split_data(posts)

    index_name = "ai-alignment-forum"
    if index_name not in rag.list_indexes():
        rag.create_index(index_name, dimension=384)  # HuggingFace embeddings dimension

    return Pinecone.from_documents(texts, embeddings, index_name=index_name)

def setup_rag(vectorstore):
    llm = HuggingFaceHub(repo_id="google/flan-t5-small", model_kwargs={"temperature":0.5, "max_length":512})
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())

def query_rag(qa, question):
    return qa.run(question)

def generate_daily_summary(qa, topics):
    summaries = {}
    for topic in topics:
        query = f"Summarize the latest discussions about {topic} in AI alignment"
        summary = query_rag(qa, query)
        summaries[topic] = summary
    return summaries

def update_database(vectorstore, new_posts):
    new_texts = clean_and_split_data(new_posts)
    vectorstore.add_documents(new_texts)

# This function will be called from your Scrapy spider
def process_scraped_data(posts):
    vectorstore = initialize_vectorstore(posts)
    qa = setup_rag(vectorstore)

    # Example usage
    result = query_rag(qa, "What are the main concerns about AI alignment?")
    print(result)

    user_interests = ["AI safety", "value learning", "robustness"]
    daily_summaries = generate_daily_summary(qa, user_interests)
    for topic, summary in daily_summaries.items():
        print(f"Summary for {topic}:")
        print(summary)
        print()

    return vectorstore, qa