import os
from dotenv import load_dotenv
from langchain_community.document_loaders import JSONLoader
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from pinecone import Pinecone
import json
from datetime import datetime

def get_search_query(doc, search_method='title'):
    if search_method == 'title':
        return doc['title']
    elif search_method == 'content':
        return doc['content'][:100] # Just the first 100 characters
    elif search_method == 'title_and_content':
        title = doc['title']
        content = doc['content'][:100]
        return f"{title} {content}"
    else:
        raise ValueError(f"Invalid search method: {search_method}")

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
    pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
    index_name = "ainews" # Should be the same as the index name used in the Pinecone console
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embedding)

    # Initialize LLM
    
    HUGGINGFACEHUB_API_TOKEN = os.environ['HUGGINGFACEHUB_API_TOKEN']

    repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        max_length=128,
        temperature=0.5,
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
    retrieved_docs = vectorstore.similarity_search(query, k=10)
    print(retrieved_docs)
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
    
    
    
    # combined_summaries = "".join(file_summaries)
    # overall_summary = summarize_text(combined_summaries, llm)
    # print("Overall summary of all posts:")
    # print(overall_summary)

    # save_summaries_to_json(file_summaries, overall_summary)