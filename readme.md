# 🤖 Chat IA con Pinecone y GPT-4o

Este proyecto permite consultar una base de conocimiento scrapeada (por ejemplo, de la documentación de FreeSWITCH) mediante una interfaz estilo ChatGPT, usando OpenAI GPT-4o, Pinecone como base vectorial, y Streamlit para la interfaz.

---

## 🧱 Requisitos

- Python 3.10+
- Cuenta en [OpenAI](https://platform.openai.com/signup) (con acceso a GPT‑4o)
- Cuenta en [Pinecone](https://www.pinecone.io/start/)
- Acceso a Internet

---

## 📁 Estructura del proyecto

```
/scrapping/
├── venv/                   # Entorno virtual (no se sube)
├── output.json             # Datos scrapeados
├── load_to_pinecone.py     # Carga los datos a Pinecone
├── chat_app.py             # UI de chat con Streamlit
├── .env                    # Variables privadas (no subir)
├── .env.example            # Plantilla del .env
└── requirements.txt        # Dependencias necesarias
```

---

## ⚙️ Instalación

1. Clona el proyecto:

```bash
git clone <repo-url>
cd scrapping
```

2. Crea un entorno virtual:

```bash
python -m venv venv
source venv/Scripts/activate  # o .\venv\Scripts\activate en Windows
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuración del `.env`

Copia el archivo `.env.example` a `.env` y completa tus claves:

```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX=freeswitch-docs
PINECONE_NAMESPACE=default

CHUNK_SIZE=1000
CHUNK_OVERLAP=100
BATCH_SIZE=200
```

---

## 🧪 Uso

### 1. Cargar contenido en Pinecone

Asegúrate de tener `output.json` generado. Luego ejecuta:

```bash
python load_to_pinecone.py
```

Esto divide los textos, genera embeddings con OpenAI y los sube al índice de Pinecone.

### 2. Ejecutar la interfaz de chat

```bash
streamlit run chat_app.py
```

Esto abrirá una interfaz en el navegador para interactuar con el asistente.

Puedes hacer preguntas como:

- `¿Cómo configuro FreeSWITCH para SIP?`
- `¿Dónde encuentro ejemplos para Debian?`

---

## 🧠 Tecnologías usadas

- [Streamlit](https://streamlit.io/)
- [OpenAI GPT‑4o](https://platform.openai.com/docs/models/gpt-4o)
- [Pinecone](https://www.pinecone.io/)
- [Langchain](https://www.langchain.com/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

---

## ✅ Ideas para mejorar

- Mostrar fuentes (URLs) usadas en cada respuesta
- Botón de "Limpiar historial"
- Exportar chat a Markdown o PDF
- Alternar entre GPT-3.5, GPT-4, GPT-4o

---

## 📜 Licencia

Este proyecto es de libre uso con fines educativos o personales.
