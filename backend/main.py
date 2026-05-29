from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from extractor import process_video
from rag_pipeline import build_vector_store  # <-- Naya Import
import asyncio
from concurrent.futures import ThreadPoolExecutor
from rag_pipeline import ask_question

app = FastAPI(title="Creator Analytics RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Frontend ko allow karne ke liye
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    video_a_url: str
    video_b_url: str

def process_video_sync(url: str):
    return process_video(url)

@app.get("/")
def read_root():
    return {"message": "API is running. Send POST request to /api/process-videos"}

@app.post("/api/process-videos")
async def process_videos_endpoint(request: VideoRequest):
    """
    Takes two video URLs, extracts data, and stores chunks into ChromaDB.
    """
    print(f"Processing Video A and Video B concurrently...")
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        task_a = loop.run_in_executor(pool, process_video_sync, request.video_a_url)
        task_b = loop.run_in_executor(pool, process_video_sync, request.video_b_url)
        
        video_a_data, video_b_data = await asyncio.gather(task_a, task_b)

    if video_a_data["status"] == "error":
        raise HTTPException(status_code=400, detail=f"Error in Video A: {video_a_data.get('message')}")
    if video_b_data["status"] == "error":
        raise HTTPException(status_code=400, detail=f"Error in Video B: {video_b_data.get('message')}")

    # --- NAYA LOGIC: Vector DB mein data daalo ---
    print("Chunking and Storing into Vector DB...")
    db_result = build_vector_store(video_a_data, video_b_data)

    return {
        "status": "success",
        "database": db_result,  # <-- Pata chalega DB mein kitne chunks gaye
        "video_a": video_a_data,
        "video_b": video_b_data
    }
    
class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Takes a user question and queries the RAG pipeline.
    """
    response = ask_question(request.message)
    if response["status"] == "error":
        raise HTTPException(status_code=500, detail=response["message"])
        
    return response