import os
import yaml

from langchain_community.document_loaders import JSONLoader

from dotenv import load_dotenv



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
