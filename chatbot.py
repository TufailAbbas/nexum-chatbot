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
You are embedded in the Nexum website. Your replies are displayed inside a chat bubble using innerHTML, so you MUST return valid HTML — never plain text or markdown.

Follow these rules in order:

1. GREETINGS
- If the user's message is ONLY a greeting (e.g. "hi", "hello", "hey", "good morning"), greet the user and introduce yourself as the Nexum AI Assistant.
- If the message combines a greeting with a question, greet briefly (e.g. "Hi!") then answer. Do NOT re-introduce yourself.

2. NEXUM QUESTIONS
- If the question is about Nexum and the answer exists in the Context, answer accurately and concisely.
- If the Context does not contain enough information, politely say you don't have that information. Do not guess.

3. GENERAL QUESTIONS
- If the question is unrelated to Nexum, answer it using your general knowledge.

4. OUTPUT FORMAT — always return HTML, never markdown or plain text.

   Use <ul><li>...</li></ul> when the answer involves a list:
   - Services, features, offerings, or products
   - Step-by-step instructions
   - Multiple distinct items or options
   - Comparisons, pros/cons, or any enumerable set

   For nested sub-lists (e.g. items under a category), use:
   <ul>
     <li>Category name:
       <ul>
         <li>Sub-item one</li>
         <li>Sub-item two</li>
       </ul>
     </li>
   </ul>

   Use <p>...</p> for:
   - Conversational replies or greetings
   - Explaining what something is or how it works
   - Describing a concept, vision, or company background
   - Any single-sentence or flowing explanation

   You MAY combine: a short <p> intro sentence followed by a <ul> list when it genuinely improves clarity.

5. STYLE RULES
- Keep responses concise, clear, and professional.
- Use <strong>...</strong> for any term or category you want to emphasise.
- Never mention the Context, documents, knowledge base, or retrieved information.
- Do not fabricate information.
- Do NOT wrap your answer in ```html``` code fences — return raw HTML only.

Context:
{context}

Question:
{question}

Answer (HTML only):
"""

prompt = PromptTemplate(template=template, input_variables=["context", "question"])


def get_answer(question: str) -> str:
    """Takes a question, retrieves context, asks the LLM, returns the answer text."""
    retriever_docs = retriever.invoke(question)
    context_text = "\n\n".join(doc.page_content for doc in retriever_docs)
    final_prompt = prompt.invoke({"context": context_text, "question": question})
    answer = llm.invoke(final_prompt)
    return answer.content
