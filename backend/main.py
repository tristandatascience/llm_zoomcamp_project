from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
from llama_index.llms.deepinfra import DeepInfraLLM
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.settings import Settings
from llama_index.llms.groq import Groq
from llama_index.llms.ollama import Ollama
import chromadb
import os

# FastAPI
app = FastAPI(port=9000)

# Initialize variables
llm = None
DEEPINFRA_API_KEY = os.environ.get("DEEPINFRA_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ChromaDB
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("DB_collection")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# Embedding
Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-large")

query_engine = None

# Function to initialize LLM
def initialize_llm(provider: str, api_key: str):
    global llm
    if provider == "DeepInfra":
        llm = DeepInfraLLM(model="meta-llama/Meta-Llama-3.1-8B-Instruct", api_key=api_key)
    elif provider == "Groq":
        llm = Groq(model="llama3-8b-8192", api_key=api_key)
    elif provider == "Ollama llama3.2:1b (Default)":
        llm = Ollama(model="llama3.2:1b", request_timeout=250.0 ,base_url="http://ollama:11434")   
    else:
        raise ValueError("Invalid LLM provider")
    Settings.llm = llm

# Initialize with default (Ollama)
initialize_llm("Ollama llama3.2:1b (Default)", "No Key")

# Endpoint to update LLM settings
@app.post("/update_llm_settings")
async def update_llm_settings(settings: dict):
    provider = settings.get("provider")
    api_key = settings.get("api_key")
    
    if not provider or not api_key:
        raise HTTPException(status_code=400, detail="Invalid settings")
    
    try:
        initialize_llm(provider, api_key)
        return {"message": "LLM settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update LLM settings: {str(e)}")

# Endpoint PDF 
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"./colab_data/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        transformations=[SentenceSplitter(chunk_size=1024, chunk_overlap=200)],
        embed_model=Settings.embed_model
    )
    print('indexation ok')
    global query_engine 
    query_engine = index.as_query_engine(similarity_top_k=5, response_mode="compact")
    return {"message": f"File '{file.filename}' uploaded and indexed successfully."}

# Endpoint LLM
@app.post("/chat")
async def chat(query: str):
    print("Received query:", query)
    response = query_engine.query(query)
    print("Response:", response.response)
    return {"response": response.response}
