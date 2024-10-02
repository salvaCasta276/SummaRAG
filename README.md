# AI Alignment Forum RAG System

## Deep Learning Course Project

This project implements a Retrieval-Augmented Generation (RAG) system connected to a Large Language Model (LLM) as part of the Deep Learning course.

### Overview

Our RAG system focuses on summarizing texts from the AI Alignment Forum, a platform dedicated to discussions about artificial intelligence alignment and safety. The system retrieves relevant information from the forum's posts and uses an LLM to generate concise summaries.

### Features

- Web scraping of AI Alignment Forum posts
- Text embedding and efficient retrieval
- Integration with a Large Language Model for summarization
- User-friendly interface for querying and retrieving summaries

### How it works

1. The scraper collects posts from the AI Alignment Forum.
2. Text is processed and embedded for efficient retrieval.
3. User queries with selected authors and interested topic to trigger relevant text retrieval.
4. The LLM generates summaries based on the retrieved content and user query.

### Setup and Usage

1. Install poetry:
2. Run `poetry install` to install dependencies.
3. Fill the .env file like .env.example.
4. Run `poetry run py ./ainewscraper/getPosts.py` to scrape last month posts from AI Alignment Forum.
5. Run `poetry run py WRITEPINECODE.py` to insert the posts into the database.
6. Run `poetry run py main.py` to start the llm to interact and generate summaries.

### Acknowledgements

This project uses content from the AI Alignment Forum (https://www.alignmentforum.org/) for educational purposes.
