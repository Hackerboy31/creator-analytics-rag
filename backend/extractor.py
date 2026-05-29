import os
import uuid
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def download_audio(video_url: str, output_filename: str):
    """Downloads audio from ANY video URL with a unique filename."""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_filename}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return f"{output_filename}.mp3"
    except Exception as e:
        print(f"Audio Download Error: {e}")
        return None

def get_whisper_transcript(audio_path: str):
    """Uses Groq's blazingly fast and FREE Whisper model to transcribe audio."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "[MOCK TRANSCRIPT] Groq API key missing in .env file."
    
    try:
        client = Groq(api_key=api_key)
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3", 
                file=(audio_path, audio_file.read())
            )
        return transcript.text
    except Exception as e:
        return f"Groq Whisper AI Error: {str(e)}"

def process_video(video_url: str):
    """Master function to extract metadata and transcript for ANY platform."""
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
        platform = info.get('extractor_key', 'Unknown')
        views = info.get('view_count') or info.get('play_count') or 0
        likes = info.get('like_count') or 0
        comments = info.get('comment_count') or 0
        
        engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0.0

        metadata = {
            "platform": platform,
            "video_id": info.get('id'),
            "creator": info.get('uploader'),
            "follower_count": info.get('channel_follower_count', 0),
            "views": views,
            "likes": likes,
            "comments": comments,
            "upload_date": info.get('upload_date'),
            "duration_seconds": info.get('duration'),
            "hashtags": info.get('tags', []),
            "engagement_rate": round(engagement_rate, 2)
        }

        transcript_text = ""
        
        if "youtube" in platform.lower():
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(metadata["video_id"])
                transcript = transcript_list.find_transcript(['en']) if 'en' in transcript_list._manually_created_transcripts else transcript_list.find_generated_transcript(['en'])
                transcript_text = " ".join([t['text'] for t in transcript.fetch()])
            except Exception:
                pass 

        if not transcript_text:
            print(f"Downloading audio for AI Transcription ({platform})...")
            unique_filename = f"temp_audio_{uuid.uuid4().hex}"
            audio_file = download_audio(video_url, unique_filename)
            
            if audio_file:
                transcript_text = get_whisper_transcript(audio_file)
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            else:
                transcript_text = "Failed to extract audio or transcript."

        return {
            "status": "success",
            "metadata": metadata,
            "transcript": transcript_text
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}