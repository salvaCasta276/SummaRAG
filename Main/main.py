import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
import yaml
from retriever import Retriever
from summarizer import Summarizer
from langchain_huggingface import HuggingFaceEndpoint

with open('config.yaml') as f:
    config = yaml.safe_load(f)

    
load_dotenv()


pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index = pc.Index(config['index_name'])
embedding = HuggingFaceEmbeddings(model_name=config['embed_name'])
authors = ['Connor Kissane', 'Buck Shlegeris']
filter_condition = {'author': {'$in': authors}}
topic = 'mass extintion'

retriever = Retriever(embedding, index)
retrieved_titles = retriever.retrieve(topic, filter_condition)

HUGGINGFACEHUB_API_TOKEN = os.environ['HUGGINGFACEHUB_API_TOKEN']
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    max_length=config['out_max_length'], 
    temperature=config['temperature'], #+ temp + aleatorio, entre 0 y 1
    token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
)

summarizer = Summarizer(llm)

summaries = dict()
for title in retrieved_titles:
    summaries[title] = summarizer.summarize_chunks(retrieved_titles[title][1])

for title in retrieved_titles:
    print(title, 'summ:', summaries[title])
    print('\n')