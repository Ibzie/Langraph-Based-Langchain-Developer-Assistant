# Langraph-Based Langchain Developer Assistant

The Langraph-Based Langchain Developer Assistant is a Retrieval-Augmented Generation (RAG) application built using the `langraph` library. This tool helps developers by allowing them to scrape Langchain documentation (or any other specified documentation) and query it for debugging, coding assistance, and general information. It utilizes Ollama Phi Llama 3.1 for content generation with local models.

## Features

- **Documentation Scraping**: Automatically scrape Langchain documentation or other specified sources.
- **Query Assistance**: Retrieve relevant information and suggestions based on user queries.
- **Content Generation**: Generate answers and content using local models.
- **Customizable**: Configure sources and settings to tailor the assistant to your needs.

## Installation

To install and set up the Langraph-Based Langchain Developer Assistant, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Ibzie/Langraph-Based-Langchain-Developer-Assistant.git
   cd Langraph-Based-Langchain-Developer-Assistant
2. **Set Up a Virtual Environment:**

    ```
    python3 -m venv .venv
    source .venv/bin/activate
3. **Install Dependencies:**
    ```
    pip install -r requirements.txt
4. **Obtain Langchain API Key:**    
    - Visit the Langchain API website to register and obtain your API key.
    - Once you have your API key, create a .env file in the root of your project directory.
5. **Configure Your Environment:**

    - Add the following lines to your .env file, replacing YOUR_API_KEY with the API key you obtained:
    ```
    LANGCHAIN_API_KEY=YOUR_API_KEY
6. **Run the Application:**

    ```
    python app.py
## Usage

1. Start the Application:

2. Run the app.py script. It will start the application and scrape the specified documentation.

3. Interact with the Assistant:

    - Enter your query when prompted. The assistant will provide relevant information based on the documentation and the query.

4. Customize:
    - Modify config.py to change settings such as URLs to scrape, depth of scraping, and local model configuration.

## Requirements
Python 3.10 or higher
Ollama Phi Llama 3.1

## Install the required packages using:
```
pip install -r requirements.txt
```
## License
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request to contribute.

## Contact
For any questions or feedback, please reach out!