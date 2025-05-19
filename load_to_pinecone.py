import os
import json
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore as LangchainPinecone
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone as pc_client, ServerlessSpec
from tqdm import tqdm

# 📥 Cargar variables de entorno
load_dotenv()

# 🔐 API keys y configuración
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")

# 🔧 Configuraciones dinámicas
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 200))

# ✅ Validar configuración base
if not all([OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX]):
    raise ValueError("❌ Faltan variables críticas en el .env")

# 🧠 Inicializar modelo de embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=OPENAI_API_KEY
)

# 🌲 Cliente Pinecone
pc = pc_client(api_key=PINECONE_API_KEY)

# Crear índice si no existe
if PINECONE_INDEX not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT)
    )

index = pc.Index(PINECONE_INDEX)

# 📄 Leer los documentos
with open("output.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

docs = [
    Document(page_content=entry["text"], metadata={"source": entry["url"]})
    for entry in raw_data if "text" in entry and entry["text"].strip()
]

print(f"📄 {len(docs)} documentos cargados.")

# ✂️ Dividir los documentos
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
docs_split = splitter.split_documents(docs)

print(f"🔹 {len(docs_split)} fragmentos generados.")

# 📦 Subida en lotes
vectorstore = LangchainPinecone(
    embedding=embedding_model,
    index_name=PINECONE_INDEX,
    namespace=PINECONE_NAMESPACE
)

for i in tqdm(range(0, len(docs_split), BATCH_SIZE), desc="📤 Subiendo a Pinecone"):
    batch = docs_split[i:i + BATCH_SIZE]
    vectorstore.add_documents(batch)

print("✅ Embeddings subidos exitosamente por lotes.")
