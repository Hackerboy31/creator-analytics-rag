from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from extractor import process_video

app = FastAPI(title="Creator Analytics RAG API")

# Define the data format we expect from the user
class VideoRequest(BaseModel):
    video_a_url: str
    video_b_url: str

@app.get("/")
def read_root():
    return {"message": "API is running. Send POST request to /api/process-videos"}

@app.post("/api/process-videos")
def process_videos_endpoint(request: VideoRequest):
    """
    Takes two video URLs (YouTube/Instagram), extracts metadata & transcripts.
    """
    print(f"Processing Video A: {request.video_a_url}")
    video_a_data = process_video(request.video_a_url)
    
    print(f"Processing Video B: {request.video_b_url}")
    video_b_data = process_video(request.video_b_url)

    if video_a_data["status"] == "error":
        raise HTTPException(status_code=400, detail=f"Error in Video A: {video_a_data.get('message')}")
    if video_b_data["status"] == "error":
        raise HTTPException(status_code=400, detail=f"Error in Video B: {video_b_data.get('message')}")

    return {
        "status": "success",
        "video_a": video_a_data,
        "video_b": video_b_data
    }