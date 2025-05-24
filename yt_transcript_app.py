import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    """Extract the video ID from a YouTube URL."""
    try:
        parsed = urlparse(url)
        if parsed.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(parsed.query).get('v', [None])[0]
        elif parsed.hostname == 'youtu.be':
            return parsed.path.lstrip('/')
        return None
    except Exception:
        return None

def fetch_transcript(video_id):
    """Fetch transcript using the correct Transcript object API."""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)

        # Use dot notation to access text
        full_text = "\n".join([entry.text for entry in transcript])
        return full_text

    except Exception as e:
        return f"Error retrieving transcript: {e}"

# --- Streamlit UI ---
st.set_page_config(page_title="YouTube Transcript Extractor", layout="centered")
st.title("📼 YouTube Transcript Extractor")
st.write("Paste a YouTube video URL below to fetch the transcript (if captions are available).")

youtube_url = st.text_input("🔗 YouTube Video URL")

if youtube_url:
    video_id = get_video_id(youtube_url)

    if not video_id:
        st.error("⚠️ Invalid or unrecognized YouTube URL.")
    else:
        with st.spinner("Fetching transcript..."):
            result = fetch_transcript(video_id)
        st.subheader("📝 Transcript")
        st.text_area("Transcript", result, height=400)
