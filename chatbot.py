import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ---- Your original notebook code, exactly as it was ----

loader = PyMuPDFLoader("NEXUM.pdf")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(docs)

embedding = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

if os.path.exists("faiss_index"):
    vectorstores = FAISS.load_local(
        "faiss_index",
        embedding,
        allow_dangerous_deserialization=True
    )
else:
    vectorstores = FAISS.from_documents(
        documents=chunks,
        embedding=embedding
    )
    vectorstores.save_local("faiss_index")

retriever = vectorstores.as_retriever(search_type="similarity", search_kwargs={"k": 4})

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)

template = """
You are a professional and helpful AI assistant for Nexum.

Your primary goal is to answer the user's questions based on the provided context if applicable, but you are also capable of answering general questions professionally.

Rules:
1. If the user sends a standard greeting (e.g., "hi", "hello", "how are you"), respond politely, introduce yourself as the Nexum AI assistant, and ask how you can help them today.
2. If the user asks a question related to Nexum, prioritize using the information provided in the Context to answer.
3. If the user asks a general question or something unrelated to Nexum, answer it professionally and accurately to the best of your general knowledge.
4. If multiple pieces of context are relevant to a Nexum-related question, combine them into one cohesive answer.
5. Keep your answer concise, friendly, and highly professional.
6. NEVER mention "the provided context", "based on the context", or similar phrases in your response. Answer naturally and confidently as if you inherently know the information.

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
