from youtube_transcript_api import YouTubeTranscriptApi

video_id = "ASFPzWtDb-M"

try:
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)

    # Use dot notation to access text
    full_text = " ".join([entry.text for entry in transcript])

    print(full_text)

except Exception as e:
    print(f"Error retrieving transcript: {e}")
