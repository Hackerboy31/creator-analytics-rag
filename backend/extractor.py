import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

def get_youtube_data(video_url: str):
    """
    Extracts metadata and transcript from a YouTube video URL.
    """
    try:
        # 1. Extract Metadata using yt-dlp
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
        metadata = {
            "platform": "YouTube",
            "video_id": info.get('id'),
            "creator": info.get('uploader'),
            "follower_count": info.get('channel_follower_count'), # Subscribers
            "views": info.get('view_count'),
            "likes": info.get('like_count'),
            "comments": info.get('comment_count'),
            "upload_date": info.get('upload_date'),
            "duration_seconds": info.get('duration'),
            "hashtags": info.get('tags', [])
        }

        # 2. Extract Transcript using a more robust method
        video_id = metadata["video_id"]
        transcript_text = ""
        try:
            # list_transcripts is much safer and handles auto-generated captions too
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                # Pehle manual english subtitles try karo
                transcript = transcript_list.find_transcript(['en'])
            except:
                # Agar manual nahi hai, toh auto-generated uthao
                transcript = transcript_list.find_generated_transcript(['en'])
                
            transcript_data = transcript.fetch()
            transcript_text = " ".join([t['text'] for t in transcript_data])
            
        except Exception as e:
            # Agar koi object attribute error aaye library ki wajah se
            try:
                api = YouTubeTranscriptApi()
                transcript_data = api.get_transcript(video_id)
                transcript_text = " ".join([t['text'] for t in transcript_data])
            except Exception as inner_e:
                transcript_text = f"Could not fetch transcript: {str(inner_e)}"

        # 3. Calculate Engagement Rate = (likes + comments) / views * 100
        views = metadata.get("views") or 0
        likes = metadata.get("likes") or 0
        comments = metadata.get("comments") or 0
        
        if views > 0:
            engagement_rate = ((likes + comments) / views) * 100
        else:
            engagement_rate = 0.0

        metadata["engagement_rate"] = round(engagement_rate, 2)

        return {
            "status": "success",
            "metadata": metadata,
            "transcript": transcript_text
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# Testing the function directly
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Example video
    print("Extracting data... Please wait.")
    result = get_youtube_data(test_url)
    
    # Printing formatted output so it's readable
    print("\n--- METADATA ---")
    for key, value in result['metadata'].items():
        print(f"{key}: {value}")
        
    print("\n--- TRANSCRIPT (First 200 chars) ---")
    print(result['transcript'][:200] + "..." if len(result['transcript']) > 200 else result['transcript'])