import os
import logging
from dotenv import load_dotenv

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ---- Vector Store & LLM Initialization ----

embedding = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

if os.path.exists("faiss_index"):
    logger.info("Loading existing FAISS index...")
    vectorstores = FAISS.load_local(
        "faiss_index",
        embedding,
        allow_dangerous_deserialization=True
    )
    logger.info("FAISS index loaded successfully.")
else:
    logger.info("FAISS index not found. Building index from NEXUM.pdf...")
    loader = PyMuPDFLoader("NEXUM.pdf")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    vectorstores = FAISS.from_documents(
        documents=chunks,
        embedding=embedding
    )
    vectorstores.save_local("faiss_index")
    logger.info("FAISS index built and saved successfully.")

retriever = vectorstores.as_retriever(search_type="similarity", search_kwargs={"k": 4})

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)

template = """
You are a friendly, professional, and polite AI assistant for Nexum.

Follow these rules in order:

1. GREETINGS
- If the user's message contains only a greeting (such as "hi", "hello", "hey", or "good morning") and no question or request, politely introduce yourself as the Nexum AI assistant.
- If the greeting is followed by a question or request, do NOT introduce yourself. Simply answer the question.

2. NEXUM QUESTIONS
- If the question is about Nexum and the answer exists in the Context, answer accurately and concisely.
- If the Context does not contain enough information, politely say that you don't have that information. Do not guess or make up facts.

3. GENERAL QUESTIONS
- If the question is unrelated to Nexum, answer it normally using your general knowledge.

4. STYLE
- Keep responses concise, clear, and professional.
- Never mention the Context, documents, knowledge base, or retrieved information.
- Do not fabricate information.

Context:
{context}

Question:
{question}

Answer:
"""

prompt = PromptTemplate(template=template, input_variables=["context", "question"])


def get_answer(question: str) -> str:
    """Takes a question, retrieves context, asks the LLM, returns the answer text."""
    retriever_docs = retriever.invoke(question)
    context_text = "\n\n".join(doc.page_content for doc in retriever_docs)
    final_prompt = prompt.invoke({"context": context_text, "question": question})
    answer = llm.invoke(final_prompt)
    return answer.content
