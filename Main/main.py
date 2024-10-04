import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone
import yaml
from retriever import Retriever
from summarizer import Summarizer
from langchain_huggingface import HuggingFaceEndpoint
from enum import Enum

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
    
def save_summary(title, author, urls, summary, folder="summaries"):
    """
    Save the summary to a file in the specified folder.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Create a valid filename from the title
    filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = filename[:50]  # Limit filename length
    filepath = os.path.join(folder, f"{filename}.txt")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Title: {title}\n")
        f.write(f"Author: {author}\n")
        f.write(f"Urls: {urls}\n\n")
        f.write(f"Summary:{summary}")
    
    print(f"Summary saved to {filepath}")

class Strictness(Enum):
    none = 0
    low = 0.5
    mid = 1
    high = 3

    def __str__(self):
        if self == Strictness.mid:
            return self.name + ' (default)'
        return self.name

def main():
    config = load_config()
    index = initialize_pinecone(config)
    embedding = HuggingFaceEmbeddings(model_name=config['embed_name'])
    retriever = Retriever(embedding, index)
    llm = initialize_llm(config)
    summarizer = Summarizer(llm)

    while True:
        selected_authors = input("Enter the authors you're interested in (comma-separated) [press enter for all authors]: ")
        selected_authors_list = []
        if selected_authors != '':
            selected_authors_list = [author.strip() for author in selected_authors.split(',')]

        topic = input("Enter the topic you're interested in: ")

        print("How strict would you like the matches to be?")
        for e in Strictness:
            print(e)
        threshold = -1
        while threshold < 0:
            strict = input("Enter strictness: ")
            if strict in Strictness.__members__:
                threshold = Strictness[strict].value
            if strict == '':
                threshold = Strictness.mid.value
            if threshold < 0:
                print('The specified stricness is invalid, please retry!')


        filter_condition = {'author': {'$in': selected_authors_list}} if len(selected_authors_list) > 0 else {}
        retrieved_titles = retriever.retrieve(topic, filter_condition, threshold)

        if not retrieved_titles:
            print("No results found for the given authors and topic.")
        else:
            # print(retrieved_titles.items())
            for title, (_, content) in retrieved_titles.items():
                # print('Content:', content)
                summary = summarizer.summarize_chunks(content, topic)
                # print('Summary:', summary)
                print("Article found:")
                print(f"\n- Title: {title}")
                if selected_authors:
                    print(f"- Author: {selected_authors}")
                else:
                    print("- Author: All")
                # print(f"Summary about the post: {summary}\n")
                # todo: author is a float, need to used it to get the most similar author
                author = selected_authors if selected_authors else "All"
                urls = {}
                for rd in content:
                    if rd['metadata']['url'] not in urls:
                        urls[rd['metadata']['url']] = True
                save_summary(title, author, "\n".join(urls.keys()), summary)
        
        continue_search = input("Do you want to perform another search? (y/n): ")
        if continue_search.lower() != 'y':
            break

if __name__ == "__main__":
    main()