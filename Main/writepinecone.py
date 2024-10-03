import os
import yaml

from dotenv import load_dotenv
from pinecone import Pinecone
from embedding_type import EmbeddingType
from db_handler import DBHandler
from preprocessor import Preprocessor


with open('config.yaml') as f:
    config = yaml.safe_load(f)
load_dotenv()

index_name = config['index_name']

#Se agarra la instancia de pinecone y el indice
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])

#Se instancia el dbhandler para crear y cargar el indice y el preprocessor para procesar el directorio con archivos
embedding_type = EmbeddingType.HuggingFace
preprocessor = Preprocessor()
db_handler = DBHandler(pc, embedding_type, index_name=index_name)

#Procesamos el dir, reiniciamos el indice y los cargamos con esta data
print('Processing data into Pinecone index')
all_chunks = preprocessor.process_dir(config['dir_path'])
print('Resetting Pinecone index')
db_handler.reset_index()
print('Inserting data into Pinecone index')
db_handler.insert_data(all_chunks)
print('Data loaded to Pinecone index')