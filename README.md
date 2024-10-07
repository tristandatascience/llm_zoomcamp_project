# llm_zoomcamp_project

This project implements a Retrieval-Augmented Generation (RAG) system that allows querying PDF or text documents using a Large Language Model (LLM) such as LLaMA hosted on DeepInfra, Groq, or locally with Ollama.

## Features

- Upload PDF or text documents
- Automatic document indexing
- Chat interface to ask questions about document content
- Utilization of an LLM to generate contextual responses
- Visualization of user feedback statistics

## Prerequisites

- Docker
- Docker Compose
- Python

## Installation and Setup

1. Clone this repository:

        `git clone https://github.com/tristandatascience/llm_zoomcamp_project.git`
        
        `cd llm_zoomcamp_project-main`

2. Make the entrypoint script for Ollama executable:

        `chmod +x frontend/entrypoint.sh`

3. Build Docker images:

          `docker-compose build`

4. Start the containers:

          `docker-compose up -d`

5. Access the user interface:
          Open your browser and go to `http://localhost:8501`

6. wait at least 5 minutes for all containers to be launched, otherwise the front will return a connection error to the services

## Usage

1. In the user interface, use the "Upload PDF" tab to upload your documents.
2. Switch to the "Chat" tab to start asking questions about your document content and leave feedback.
3. You can view feedback statistics in the "Feedback and Statistics" tab.

## Configuration

The project uses environment variables for configuration. You can modify them in the docker-compose.yml file (API keys for LLMs).

## LLM Options

This project supports three LLM providers:

1. DeepInfra
2. Groq
3. Ollama (local)

Please note that when using the local model with Ollama, it's recommended to use smaller files with very few pages. Processing times with Ollama will be significantly longer compared to Groq or DeepInfra. For optimal performance with larger documents, consider using Groq or DeepInfra.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
