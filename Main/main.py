import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
import yaml
from retriever import Retriever
from summarizer import Summarizer
from langchain_huggingface import HuggingFaceEndpoint
from embedding_type import EmbeddingType
from db_handler import DBHandler
from preprocessor import Preprocessor

with open('config.yaml') as f:
    config = yaml.safe_load(f)
load_dotenv()

index_name = config['index_name']

#Se agarra la instancia de pinecone y el indice
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index = pc.Index(index_name)

#Se instancia el dbhandler para crear y cargar el indice y el preprocessor para procesar el directorio con archivos
embedding_type = EmbeddingType.HuggingFace
preprocessor = Preprocessor()
db_handler = DBHandler(pc, embedding_type, index_name=index_name)

#Procesamos el dir, reiniciamos el indice y los cargamos con esta data
all_chunks = preprocessor.process_dir(config['dir_path'])
db_handler.reset_index()
db_handler.insert_data(all_chunks)

#Definimos los filtros para hacer la busqueda sobre la db
embedding = HuggingFaceEmbeddings(model_name=config['embed_name'])
authors = ['Connor Kissane', 'Buck Shlegeris']
filter_condition = {'author': {'$in': authors}}
topic = 'mass extintion'

#Instanciamos el retriever para buscar en la db
retriever = Retriever(embedding, index)
retrieved_titles = retriever.retrieve(topic, filter_condition)

#Instanciamos el llm para hacer los resumenes
HUGGINGFACEHUB_API_TOKEN = os.environ['HUGGINGFACEHUB_API_TOKEN']
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    max_length=config['out_max_length'], 
    temperature=config['temperature'], #+ temp + aleatorio, entre 0 y 1
    token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
)

#Instanciamos el summarizer y hacemos un resumen por publicacion
summarizer = Summarizer(llm)

summaries = dict()
for title in retrieved_titles:
    summaries[title] = summarizer.summarize_chunks(retrieved_titles[title][1])

for title in retrieved_titles:
    print(title, 'summ:', summaries[title])
    print('\n')