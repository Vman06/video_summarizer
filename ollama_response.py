import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import ollama  # Import the ollama library


# --- YouTube Transcript Extraction Functions ---
def get_video_id(url):
    """Extract the video ID from a YouTube URL."""
    try:
        parsed = urlparse(url)
        # Handle different YouTube URL formats
        if parsed.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(parsed.query).get('v', [None])[0]
        elif parsed.hostname == 'youtu.be':
            return parsed.path.lstrip('/')
        return None
    except Exception:
        return None


def fetch_transcript(video_id):
    """Fetch transcript using the youtube_transcript_api library."""
    try:
        print(video_id)
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id)
        full_text = "\n".join([snippet.text for snippet in transcript_list])
        return full_text
    except Exception as e:
        return f"Error retrieving transcript: {e}"


# --- Ollama Model Interaction Function ---
def summarize_with_ollama(transcript_text, model_name="llama2"):
    """Sends the transcript to a local Ollama model for summarization."""
    summarization_prompt_template = """
    Summarize the following meeting transcript, giving headlines on important sub-topics.
    For each sub-topic, include:
    - **Topic Name:** A clear, concise headline for the sub-topic.
    - **Speakers:** List all speakers who contributed to this sub-topic.
    - **Summary:** A brief summary of the discussions and decisions for this sub-topic.
    - **Public Comments:** Detail any public comments specifically related to this sub-topic, including the speaker name if available.
    - **Key Takeaways:** List 1-3 key insights or outcomes for this sub-topic.

    Ensure the output is well-structured and easy to read.
    Do not include any introductory or concluding remarks outside of the requested format.

    Display in a proper format with new line

    --- MEETING TRANSCRIPT ---
    {transcript}
    --- END OF TRANSCRIPT ---
    """
    full_prompt = summarization_prompt_template.format(transcript=transcript_text)

    try:
        # Make sure your Ollama server is running (e.g., `ollama run llama2`)
        # and the model you specified is downloaded.
        response = ollama.chat(
            model=model_name,
            messages=[
                {'role': 'user', 'content': full_prompt},
            ],
            # You might adjust options like temperature or max_tokens for different results
            # options={'temperature': 0.7, 'num_predict': 1024}
        )
        return response['message']['content']
    except ollama.ResponseError as e:
        return f"Error from Ollama: {e.error}. Please ensure Ollama is running and the specified model is downloaded."
    except Exception as e:
        return f"An unexpected error occurred with Ollama: {e}. Double-check your Ollama setup and model name."


# --- Streamlit UI Starting---
st.set_page_config(page_title="YouTube Transcript & Ollama Summarizer", layout="centered")
st.title("📼 YouTube Transcript & Local Ollama Summarizer")
st.write("Paste a YouTube video URL to fetch its transcript, then summarize it using your local Ollama model.")

# Initialize session state variables if they don't exist
if 'transcript_result' not in st.session_state:
    st.session_state.transcript_result = None
if 'ollama_model_name' not in st.session_state:
    st.session_state.ollama_model_name = None  # Default value

youtube_url = st.text_input("🔗 YouTube Video URL", key="youtube_url_input")

if youtube_url:
    video_id = get_video_id(youtube_url)

    if not video_id:
        st.error("⚠️ Invalid or unrecognized YouTube URL.")
        st.session_state.transcript_result = None  # Clear previous transcript on invalid URL
    else:
        # Only fetch if URL changed or no transcript yet
        if st.session_state.get('last_youtube_url') != youtube_url or st.session_state.transcript_result is None:
            with st.spinner("Fetching transcript..."):
                st.session_state.transcript_result = fetch_transcript(
                    video_id)  # Get Transcript from API and Save it session variable
            st.session_state.last_youtube_url = youtube_url  # Store last URL for change detection

        st.subheader("📝 Fetched Transcript")
        if st.session_state.transcript_result and "Error" in st.session_state.transcript_result:
            st.error(st.session_state.transcript_result)
            st.session_state.transcript_result = None  # Clear transcript if there was an error
        elif st.session_state.transcript_result:
            st.text_area("Transcript", st.session_state.transcript_result, height=300, key="youtube_transcript_display")
        else:
            st.info("No transcript available or fetched yet for this URL.")

# --- Ollama Integration ---
if st.session_state.transcript_result is not None:  # Only show Ollama options if a transcript was successfully fetched
    st.markdown("---")
    st.subheader("Summarize with Local Ollama Model")

    # Use session state for model name input
    ollama_model_name_input = st.selectbox(
        "Choose Ollama Model",
        options=["llama2", "mistral", "qwen3:8b", "qwen3:32b", "custom..."],
        index=0
    )
    # Update session state when the input changes
    if ollama_model_name_input != st.session_state.ollama_model_name:
        st.session_state.ollama_model_name = ollama_model_name_input

    if st.button("Summarize Transcript with Ollama", type="primary"):
        if not st.session_state.ollama_model_name:
            st.error("Please enter an Ollama Model Name.")
        elif not st.session_state.transcript_result:
            st.error("No transcript available to summarize. Please fetch a transcript first.")
        else:
            with st.spinner(
                    f"Sending transcript to local Ollama model '{st.session_state.ollama_model_name}'... This may take a moment."):
                ollama_summary = summarize_with_ollama(
                    st.session_state.transcript_result,
                    st.session_state.ollama_model_name
                )

            if "Error" in ollama_summary:
                st.error(ollama_summary)
            else:
                st.subheader(f"Summary from Ollama Model: {st.session_state.ollama_model_name}")
                st.markdown(ollama_summary)  # Use markdown to render formatted text
                st.success("Summarization complete!")

st.markdown("---")
st.markdown(
    "This application requires a local Ollama instance running. Ensure Ollama is installed, running, and you have the specified model downloaded (e.g., `ollama run llama2`).")
