import os
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
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

    def summarize_chunks(self, chunks):
        try:
            text = " ".join(rd['metadata']['text'] for rd in chunks)
            chain = load_summarize_chain(self.llm, chain_type="stuff")
            doc = Document(page_content=text)
            summary = chain.invoke([doc])
            return summary['output_text']
        except Exception as e:
            print(f"Error in summarization: {e}")
            return "Error in summarization"
