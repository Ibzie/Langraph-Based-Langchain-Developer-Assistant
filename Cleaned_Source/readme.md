# Langchain Bot

Langchain Bot is a Python application that utilizes Langchain to create a Retrieval-Augmented Generation (RAG) system. The application scrapes URLs, loads and processes documents, and uses a state graph to handle various stages of document retrieval, grading, and generation.

## Features

- Scrapes URLs for document extraction.
- Loads and splits documents for processing.
- Creates and uses a vector store for document retrieval.
- Uses prompt templates and LLMs for grading and generating responses.
- Interactive CLI to query the system and get answers.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Ibzie/Langchain-Bot
    cd project0anem
    ```

2. Create a virtual environment:
    ```bash
    python -m venv .venv
    ```

3. Activate the virtual environment:
    - On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    - On Unix or MacOS:
        ```bash
        source .venv/bin/activate
        ```

4. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

- **`config.py`**: Contains configurations for LLM, starting URL, and maximum depth for URL scraping.

## Usage

1. Run the application:
    ```bash
    python app.py
    ```

2. Follow the prompts to enter your query. Type `\q` or `\Q` to quit.

## Requirements

Ensure that you have CUDA 11.5 or a compatible version installed for GPU support if needed.

## Troubleshooting

If you encounter issues related to dependencies or configurations, please consult the [Langchain documentation](https://python.langchain.com/).

## License

This project is licensed under the MIT License
