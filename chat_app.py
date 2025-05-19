import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone as pc_client
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 📥 Cargar variables desde .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")

# 🧠 Embeddings y conexión a Pinecone
pc = pc_client(api_key=PINECONE_API_KEY)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)
vectorstore = PineconeVectorStore(
    embedding=embedding_model,
    index_name=PINECONE_INDEX,
    namespace=PINECONE_NAMESPACE
)

# 📌 Prompt personalizado
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Eres un asistente técnico especializado en documentación de FreeSWITCH y haces consultas a la base de datos vectorial."

Usa formato Markdown en tu respuesta.
Si la respuesta incluye código, muéstralo dentro de bloques de código.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""
)

# 💬 Inicializar modelo de lenguaje y RAG
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    openai_api_key=OPENAI_API_KEY
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)

# 🖼️ Interfaz Streamlit
st.set_page_config(page_title="Chat RAG con Pinecone", layout="wide")
st.title("🤖 Chat IA sobre documentación FreeSWITCH")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.chat_input("Haz una pregunta sobre la documentación...")

if query:
    with st.spinner("Pensando..."):
        result = qa_chain.invoke({"query": query})
        st.session_state.chat_history.append((query, result["result"]))

# 📝 Mostrar historial
for user_input, response in st.session_state.chat_history:
    st.markdown(f"**🧑 Tú:** {user_input}")
    st.markdown(f"**🤖 IA:**\n\n{response}", unsafe_allow_html=True)
