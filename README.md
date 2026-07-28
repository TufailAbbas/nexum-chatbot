# Nexum RAG Chatbot — README

A Retrieval-Augmented Generation (RAG) chatbot that answers questions
about Nexum Global Solutions using content from `NEXUM.pdf`.

## How it works
- **LangChain** handles the RAG pipeline
- **HuggingFace embeddings** (`all-MiniLM-L6-v2`) embed the document chunks
- **FAISS** stores and searches those embeddings
- **Groq** (`llama-3.1-8b-instant`) generates the final answer
- **FastAPI** exposes it all as a web API so a website can call it

## Files
| File | What it does |
|---|---|
| `chatbot.py` | Your original RAG logic: loads `NEXUM.pdf`, splits it into chunks, builds the FAISS index, and defines `get_answer(question)` which retrieves relevant chunks and asks the LLM |
| `app.py` | The web server. Imports `chatbot.py` and exposes it as an API with a `POST /chat` endpoint |
| `requirements.txt` | All Python packages needed to run this |
| `.env` | Holds your `GROQ_API_KEY` (never share or commit this file) |
| `NEXUM.pdf` | The source document the chatbot answers from |
| `faiss_index/` | The saved vector index (auto-created the first time `app.py` runs) |

## Running it locally

1. **Create and activate a virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   *(If PowerShell blocks this, run once:
   `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`)*

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Add your Groq API key**
   Create a `.env` file in this folder containing:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
   Get a key at https://console.groq.com

   > ⚠️ If a Groq key was ever shared publicly (e.g. pasted in a chat or
   > notebook), treat it as compromised and generate a new one.

4. **Run the server**
   ```powershell
   uvicorn app:app --reload --port 8000
   ```

5. **Test it**
   - Health check: open http://localhost:8000 in your browser → `{"status": "ok"}`
   - Interactive docs: open http://localhost:8000/docs → click `/chat` → "Try it out" → type a question → "Execute"
   - Or from a second terminal:
     ```powershell
     Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -ContentType "application/json" -Body '{"question": "what services does nexum offer"}'
     ```

   Note: `/chat` only accepts `POST` requests, so visiting
   `http://localhost:8000/chat` directly in a browser will show
   "405 Method Not Allowed" — that's expected, not a bug.

## Deploying so a website can use it

Running locally only works on your own machine. To give the instructor
a live URL the website can call:

1. **Push this project to GitHub** (a `.gitignore` should exclude `.env`
   and `venv/` so your key and local files aren't uploaded)
2. **Deploy on Render** (or Railway):
   - Connect your GitHub repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Add `GROQ_API_KEY` as an environment variable in the platform's dashboard (not in the code)
3. Render gives you a public URL, e.g. `https://nexum-chatbot.onrender.com`

## Giving it to the instructor

Once deployed, all the instructor needs is the URL:
```
POST https://nexum-chatbot.onrender.com/chat
Body: { "question": "..." }
Response: { "answer": "..." }
```
Their website's JavaScript calls this endpoint directly — no code, no
API key, no setup needed on their side.

## Updating the chatbot's knowledge
To change what the bot knows, replace `NEXUM.pdf` with an updated
version and delete the `faiss_index/` folder — it will be rebuilt
automatically the next time `app.py` starts.
