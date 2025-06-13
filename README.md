# Video Summarizer

### This project is build using streamlit and python
### It gets transcripts from youtube links
### Use the transcripts to get a summary of the video using Models via Ollama

## How to Run

### Install python virtual environment
```
python3 -m venv venv
```
### Activate python virtual environment
```
source venv/bin/activate
```

### Install python dependencies to virtual environment
```
pip install -r requirements.txt
```

### Run Streamlit APP
```
streamlit run ollama_response.py
```

### To run Ollama in terminal (Optional)
```
ollama run qwen3:8b
```