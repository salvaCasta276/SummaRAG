import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from pinecone import Pinecone
import yaml


with open('config.yaml') as f:
    config = yaml.safe_load(f)


class AgregationDict(dict):
    def agregate(self, name, value):
        if self.get(name) is None:
            self[name] = value
        else:
            self[name] = [a + b for a, b in zip(value, self.get(name))]
    def over_boundry(self, boundry):
        titles = dict()
        for title in self:
            if self.get(title)[0] >= boundry:
                titles[title] = self.get(title)
        return titles

class Retriever:
    def __init__(self, embedding, index):
        self.embedding = embedding
        self.index = index


    def retrieve(self, query, filter_condition):

        results = self.index.query(vector=self.embedding.embed_query(query), top_k=config['num_retrievals'], include_metadata=True, filter=filter_condition)

        score_counter = AgregationDict()
        for match in results['matches']:
            score_counter.agregate(match['metadata']['title'], [match['score'], [match]])

        return score_counter.over_boundry(config['match_boundry'])

    
load_dotenv()

pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index = pc.Index(config['index_name'])
embedding = HuggingFaceEmbeddings(model_name=config['embed_name'])
authors = ['Connor Kissane', 'Buck Shlegeris']
filter_condition = {'author': {'$in': authors}}
topic = 'mass extintion'

retriever = Retriever(embedding, index)
print(retriever.retrieve(topic, filter_condition))