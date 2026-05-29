# 🚀 Creator Analytics AI - RAG Video Comparison Pipeline

A full-stack AI application that compares YouTube videos/shorts by extracting audio, generating transcripts, building a local Vector Database, and answering user queries using an advanced RAG (Retrieval-Augmented Generation) pipeline.

## ✨ Features

* 🎥 **Dual Video Processing:** Input any two YouTube, Shorts, or Instagram Reels URLs for instant comparative analysis.
* 🎙️ **Lightning Fast Transcription:** Uses Groq's Whisper-large-v3 model to extract and convert video audio to text seamlessly.
* 📊 **Deep Metadata & Engagement:** Automatically pulls creator details, views, likes, comments, and computes the True Engagement Rate.
* 📚 **Local Vector Database:** Implements ChromaDB to chunk and store transcripts, automatically managing sessions for clean data.
* 🧠 **Advanced RAG Architecture:** Retrieves relevant context (chunks) and feeds it to Llama-3.1-8b for highly accurate, context-aware answers.
* ⚡ **Streaming Responses:** Provides real-time, ChatGPT-like typing effects for AI responses using FastAPI `StreamingResponse`.
* 💬 **Stateful Chat Memory:** Maintains conversation history across turns, allowing users to ask follow-up questions naturally.
* 🎯 **Source Tracking:** AI responses include interactive source citations (e.g., Video A / Video B) to verify where the information came from.
* 🎨 **Sleek UI/UX:** A responsive React (Vite) dashboard built with Tailwind CSS, featuring modern UI components and input safety locks.
## 🛠️ Tech Stack

**Frontend:**
- React (Vite)
- Tailwind CSS
- Lucide React (Icons)
- Axios & React-Markdown

**Backend & AI/ML:**
- Python & FastAPI
- LangChain (Text Splitters & Document Loaders)
- ChromaDB (Local Vector Store)
- Groq API (Llama-3.1 & Whisper)
- yt-dlp (Audio & Metadata Extraction)
- HuggingFace (`all-MiniLM-L6-v2` for Embeddings)

## 🚀 Getting Started

### Prerequisites
Make sure you have Node.js, Python 3.9+, and Git installed on your system. You will also need a free [Groq API Key](https://console.groq.com/keys).

### 1. Clone the Repository
```bash
git clone [https://github.com/Hackerboy31/creator-analytics-rag.git](https://github.com/Hackerboy31/creator-analytics-rag.git)
cd creator-analytics-rag
```

### 2. Backend Setup
Navigate to the backend folder and set up your Python environment:

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the backend folder and add your Groq API Key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Start the FastAPI server:
```bash
uvicorn main:app --reload
```
*(The backend will run on http://127.0.0.1:8000)*

### 3. Frontend Setup
Open a new terminal and navigate to the frontend folder:

```bash
cd frontend
npm install
npm run dev
```
*(The frontend will run on http://localhost:5173)*

## 💡 How to Use
1. Paste two YouTube/Shorts URLs in the "Process Videos" panel.
2. Click **"Extract & Build Vector DB"**. The system will download audio, transcribe it, chunk the text, and store it in ChromaDB.
3. Once processed, metadata cards (Views, Likes, Creator) will appear.
4. Use the Chat interface to ask comparative questions like *"Compare the hooks of both videos"* or *"What is the main advice given in Video A?"*
5. Get accurate answers powered by Llama-3.1, complete with specific source tags!

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📝 License
This project is [MIT](LICENSE) licensed.