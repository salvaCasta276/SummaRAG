import os
from dotenv import load_dotenv
from langchain_community.document_loaders import JSONLoader
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from pinecone import Pinecone
from pinecone import Index
import json
import yaml
from datetime import datetime


with open('config.yaml') as f:
    config = yaml.safe_load(f)


def summarize_text(text, llm):
    try:
        chain = load_summarize_chain(llm, chain_type="stuff")
        doc = Document(page_content=text)
        summary = chain.invoke([doc])
        return summary['output_text']
    except Exception as e:
        print(f"Error in summarization: {e}")
        return "Error in summarization"

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


if __name__ == "__main__":
    load_dotenv()

    # Initialize Pinecone and vector store
    #TODO esto se usa para algo?
    pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
    index_name = "ainews" # Should be the same as the index name used in the Pinecone console
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embedding)
    index = pc.Index(index_name)

    # Initialize LLM
    
    HUGGINGFACEHUB_API_TOKEN = os.environ['HUGGINGFACEHUB_API_TOKEN']

    repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        max_length=config['out_max_length'], 
        temperature=config['temperature'], #+ temp + aleatorio, entre 0 y 1
        token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
    )

    # Load documents (just for getting titles/metadata)
    files = os.listdir("ainewscraper/output/")
    docs = []
    for file in files:
        with open(f"ainewscraper/output/{file}", 'r', encoding='utf-8') as f:
            docs.append(json.load(f))

    # Choose search method (title, content, title_and_content) for summarization
    search_method = 'title'

    # file_summaries = []
    # for doc in docs:
    #     try:
    #         query = get_search_query(doc, search_method)
    #         retrieved_docs = vectorstore.similarity_search(query, k=10)
        
    #         file_summary = summarize_text(retrieved_docs, llm)
    #         file_summaries.append(file_summary)
    #         print(f"Summary for {doc['title']}:")
    #         print(file_summary)
    #         print("\n" + "="*50 + "\n")
    #     except Exception as e:
    #         print(f"Error processing document: {e}")
    #         continue
    
    ### TESTING WITH ONE DOCUMENT
    doc = docs[0]
    
    # check doc type
    print(type(doc))
    
    query = get_search_query(doc, search_method)

    #Se definene los autores de los que quiero recibir resumenes
    #Te sigue tranyendo la cantidad original pero solo de los autores seleccionados
    retrieved_docs = vectorstore.similarity_search(query, k=config['num_retrievals'])

    #query = 'preventing models from doing unwanted things'
    #filter_condition = {'author': {'$in': ['Connor Kissane', 'Buck Shlegeris']}}
    #results = index.query(vector=embedding.embed_query(query), top_k=config['num_retrievals'], include_metadata=True, filter=filter_condition)

    #score_counter = AgregationDict()
    #for match in results['matches']:
    #    score_counter.agregate(match['metadata']['title'], match['score'])

    #for title in score_counter:
    #    print('Title:', title)
    #    print('Score:', score_counter.get(title))
    #    print('\n')

    #print(score_counter.over_boundry(0.3))

    print("\n" + "="*50 + "\n")
    # Extract the content of the retrieved documents
    input_text = " ".join(rd.page_content for rd in retrieved_docs)
    
    print("Input text for summarization:")
    print(input_text)
    print("\n" + "="*50 + "\n")
    
    file_summary = summarize_text(input_text, llm)
    print(f"Summary for {doc['title']}:")
    print(file_summary)
    print("\n" + "="*50 + "\n")
    
    # check if summaries folder exists
    if not os.path.exists('summaries'):
        os.makedirs('summaries')
    
    with open(f"summaries/{doc['title']}-Summary.json", 'w', encoding='utf-8') as f:
        json.dump(file_summary, f, ensure_ascii=False, indent=2)
    
    
    
    #combined_summaries = "".join(file_summaries)
    #overall_summary = summarize_text(combined_summaries, llm)
    #print("Overall summary of all posts:")
    #print(overall_summary)

    #save_summaries_to_json(file_summaries, overall_summary)