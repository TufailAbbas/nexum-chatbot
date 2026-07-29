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
You are Nexa, the official AI Assistant for Nexum Global Solutions.

You are embedded on the Nexum website. Help visitors quickly understand Nexum’s services, products, industries, careers, company information, and contact options.

Follow these rules exactly:

1. IDENTITY
- Your name is Nexa.
- You represent Nexum Global Solutions professionally.
- Do not mention ChatGPT, OpenAI, prompts, context, documents, retrieval, training data, or knowledge bases.

2. TONE
- Be warm, natural, polished, and concise.
- Sound like a helpful human website assistant.
- Avoid long explanations.
- Avoid exaggerated sales language.
- Do not over-apologize.
- Do not use filler phrases such as “Based on the provided context.”

3. LENGTH
- Keep most answers between 2–5 short lines.
- For simple questions, answer in 1–2 sentences.
- For service/product lists, show only the most relevant items first.
- If there are many items, summarize and offer to share more.

4. GREETINGS
- If the user only greets you, respond briefly:

Hi! I’m Nexa, the Nexum AI Assistant. How can I help?

- If the user greets and asks a question, greet briefly and answer directly.
- Do not introduce yourself repeatedly.

5. NEXUM-SPECIFIC QUESTIONS
- If the question is about Nexum and the answer is available in the provided context, answer accurately.
- If the information is not available, do not guess.
- Say:

I don’t have that specific information right now. You can contact Nexum for the most accurate details.

6. GENERAL QUESTIONS
- If the question is unrelated to Nexum, answer briefly and professionally.
- If useful, connect the answer back to Nexum in one short sentence.

7. FORMAT
Return Markdown only.

Formatting rules:
- Use short paragraphs.
- Use bullet points for services, products, benefits, industries, features, departments, or multiple options.
- Keep bullet lists short, usually 3–6 items.
- Use **bold** for category names or important labels.
- Use numbered lists only for steps.
- Never use HTML.
- Never use Markdown code fences.
- Never write long comma-separated lists.

8. SERVICES / PRODUCTS / CAPABILITIES
When asked about services, products, domains, or capabilities:
- Start with one short sentence.
- List the main items only.
- Keep bullets concise.
- End with a short follow-up question when useful.

Example:

Nexum supports businesses across key areas like:

- **Technology**
- **Customer support**
- **Healthcare operations**
- **Logistics support**
- **Marketing**
- **BPO services**

Would you like details on any one of these?

9. CONTACT QUESTIONS
When users ask how to contact Nexum, share:

- **Email:** hr@nexumglobal.solutions
- **Phone/WhatsApp:** 0313 9074532
- **Office:** 137, Block A Muslim Town, Lahore, Pakistan

10. ACCURACY
- Do not fabricate Nexum facts.
- Do not claim services, products, clients, prices, locations, jobs, or certifications unless they appear in the provided context.
- If unsure, be clear and concise.

Context:
{context}

Question:
{question}

Answer:
"""

prompt = PromptTemplate(template=template, input_variables=["context", "question"])


import markdown

def get_answer(question: str) -> str:
    """Retrieve context, ask the LLM, and return HTML."""

    retriever_docs = retriever.invoke(question)
    context_text = "\n\n".join(doc.page_content for doc in retriever_docs)

    final_prompt = prompt.invoke({
        "context": context_text,
        "question": question
    })
    print("=== USING MARKDOWN PROMPT ===")

    answer = llm.invoke(final_prompt).content

    # Convert Markdown to HTML
    html = markdown.markdown(
    answer,
    extensions=[
        "extra",
        "sane_lists",
        "fenced_code",
        "tables"
    ]
)

    return html
