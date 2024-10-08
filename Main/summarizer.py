import os
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.summarize.chain import load_summarize_chain
from langchain_core.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
import json
import yaml
from datetime import datetime


with open('config.yaml') as f:
    config = yaml.safe_load(f)


def save_summaries_to_json(file_summaries, overall_summary):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "summaries"
    os.makedirs(output_dir, exist_ok=True)
    
    index_data = {
        "file_summaries": file_summaries,
        "overall_summary": overall_summary
    }
    
    index_filename = f"{output_dir}/index_{timestamp}.json"
    with open(index_filename, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"Summaries have been saved to {index_filename}")


class Summarizer:
    def __init__(self, llm):
        self.llm = llm

    def summarize_chunks(self, chunks, topic):
        load_dotenv()
        try:
            text = " ".join(rd['metadata']['text'] for rd in chunks)
            #engineered_prompt = "Make a summary of the following:\n\n"
            #engineered_prompt = "Write a concise summary in third person of the following content, as if making a new article but shorter:\\n\\n"
            engineered_prompt = "Write a cohesive short text in third person telling us what the author's thoughts regarding " + topic + " are in the following text:\\n\\n"
            prompt = ChatPromptTemplate.from_messages(
                [("system", engineered_prompt + "{context}")]
            )
            #chain = create_stuff_documents_chain(self.llm, prompt)
            chain = load_summarize_chain(self.llm, chain_type="stuff")
            doc = Document(page_content=text)
            docs = [Document(page_content=rd['metadata']['text']) for rd in chunks]
            #summary = chain.invoke({"context": docs})
            #return summary
            summary = chain.invoke([doc])
            return summary['output_text']
        except Exception as e:
            print(f"Error in summarization: {e}")
            return "Error in summarization"
