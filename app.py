import streamlit as st
from st_audiorec import st_audiorec
import wave
import requests
import base64
import os

# GitHub repository and token details
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Store your token securely in environment variables
GITHUB_REPO = "your-username/your-repo-name"
GITHUB_FOLDER = "audio_recordings"
GITHUB_BRANCH = "main"  # or the branch name where you want to upload

# Function to upload a file to GitHub
def upload_to_github(file_path, file_content):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FOLDER}/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Get the current file's SHA (if it exists) for updating
    response = requests.get(url, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json().get("sha")
    
    # Create the payload
    data = {
        "message": f"Add {file_path}",
        "content": base64.b64encode(file_content).decode("utf-8"),
        "branch": GITHUB_BRANCH
    }
    if sha:
        data["sha"] = sha
    
    # Upload the file
    response = requests.put(url, json=data, headers=headers)
    return response.status_code, response.json()

def audiorec_demo_app():

    st.title('Streamlit Audio Recorder')

    wav_audio_data = st_audiorec()

    if wav_audio_data is not None:
        file_name = "recorded_audio.wav"
        
        # Save the audio data locally
        with wave.open(file_name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # Assuming 16-bit audio
            wf.setframerate(44100)  # Assuming a sample rate of 44100 Hz
            wf.writeframes(wav_audio_data)
        
        # Read the saved file
        with open(file_name, "rb") as f:
            file_content = f.read()
        
        # Upload to GitHub
        status_code, response_json = upload_to_github(file_name, file_content)
        
        if status_code == 201 or status_code == 200:
            st.success(f"File uploaded successfully to GitHub! View it [here]({response_json['content']['html_url']})")
        else:
            st.error(f"Failed to upload file: {response_json.get('message', 'Unknown error')}")
        
        # Display the audio player in Streamlit
        st.audio(file_content, format='audio/wav')


if __name__ == '__main__':
    audiorec_demo_app()
