import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
import yaml
from retriever import Retriever
from summarizer import Summarizer
from langchain_huggingface import HuggingFaceEndpoint

def load_config():
    with open('config.yaml') as f:
        return yaml.safe_load(f)

def initialize_pinecone(config):
    load_dotenv()
    pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
    return pc.Index(config['index_name'])

def initialize_llm(config):
    repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
    return HuggingFaceEndpoint(
        repo_id=repo_id,
        max_length=config['out_max_length'],
        temperature=config['temperature'],
        token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
    )
    
def save_summary(title, author, summary, folder="summaries"):
    """
    Save the summary to a file in the specified folder.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Create a valid filename from the title
    filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = filename[:20]  # Limit filename length
    filepath = os.path.join(folder, f"{filename}.txt")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Title: {title}\n")
        f.write(f"Author: {author}\n\n")
        f.write(f"Summary:\n{summary}\n")
    
    print(f"Summary saved to {filepath}")

def main():
    config = load_config()
    index = initialize_pinecone(config)
    embedding = HuggingFaceEmbeddings(model_name=config['embed_name'])
    retriever = Retriever(embedding, index)
    llm = initialize_llm(config)
    summarizer = Summarizer(llm)

    while True:
        selected_authors = input("Enter the authors you're interested in (comma-separated), or 'all' for all authors: ")
        selected_authors_list = []
        if selected_authors.lower() != 'all':
            selected_authors_list = [author.strip() for author in selected_authors.split(',')]

        topic = input("Enter the topic you're interested in: ")

        filter_condition = {'author': {'$in': selected_authors_list}} if selected_authors else {}
        retrieved_titles = retriever.retrieve(topic, filter_condition)

        if not retrieved_titles:
            print("No results found for the given authors and topic.")
        else:
            for title, (author, content) in retrieved_titles.items():
                summary = summarizer.summarize_chunks(content)
                print(f"\nTitle Found: {title}")
                if selected_authors:
                    print(f"Author: {selected_authors}")
                else:
                    print("Author: All")
                print(f"Summary about the post: {summary}\n")
                # todo: author is a float, need to used it to get the most similar author
                author = selected_authors if selected_authors else "All"
                save_summary(title, author, summary)
        
        continue_search = input("Do you want to perform another search? (yes/no): ")
        if continue_search.lower() != 'yes':
            break

if __name__ == "__main__":
    main()