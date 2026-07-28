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
You are a helpful AI assistant.

You must answer the user's question using ONLY the information provided in the context.

Rules:
1. Do not make up facts.
2. Do not use your own knowledge.
3. If the context does not contain the answer, reply:
   "I could not find this information in the document."
4. If multiple pieces of context are relevant, combine them into one answer.
5. Keep your answer concise and professional.

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
