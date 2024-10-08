import yaml
from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec
import cleaning

with open('config.yaml') as f:
    config = yaml.safe_load(f)

class DBHandler:
    def __init__(self, pc, embedding_type, index_name):
        self.pc = pc
        self.embedding_type = embedding_type
        self.index_name = index_name
        self.database = None
        self._create_index()

    # Esta clase deberia ser privada pero bueno, no hay que llamarla de afuera
    def _create_index(self):
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=self.embedding_type.embedding_size,
                metric=config['metric'],
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )

        self.database = PineconeVectorStore(index_name=self.index_name, embedding=self.embedding_type.get_embedding())

    def reset_index(self):
        self.pc.delete_index(self.index_name)
        self.database = None
        self._create_index()

    def insert_data(self, data):
        self.database.add_documents(data)


def clean_text(text):
    return cleaning.clean_content(text)
