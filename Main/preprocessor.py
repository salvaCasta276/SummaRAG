import os
import yaml
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
import cleaning

# This class is used to preprocess the json files in a input directory
# The json files are expected to have the following structure:
# {
#     "content": "The content of the page",
#     "url": "The url of the page",
#     "title": "The title of the page",
#     "author": "The author of the page",
#     "date": "The date of the page"
# }
# The JSONLoader is used to load the json files and extract the content, url, title, author and date to be later uploaded to the Pinecone index
#
# The content of the page is cleaned and split into chunks of text using the RecursiveCharacterTextSplitter

with open('config.yaml') as f:
    config = yaml.safe_load(f)

class Preprocessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config['chunk_size'], 
            chunk_overlap=config['chunk_overlap'],
            add_start_index=True)

    def process_dir(self, data_path):
        files = os.listdir(data_path)
        docs_loader = []
        for file in files:
            docs_loader.append(DocumentLoader(path=data_path + file))

        all_chunks = []
        for loader in docs_loader:
            docs = loader.load()
            for doc in docs:
                doc.page_content = cleaning.clean_content(doc.page_content)

            chunks = self.text_splitter.split_documents(docs)
            all_chunks.extend(chunks)

        return all_chunks

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
