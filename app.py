import streamlit as st
from st_audiorec import st_audiorec
from google.cloud import speech_v1p1beta1 as speech
import numpy as np
import tempfile
import wave
import io
from gtts import gTTS
import base64
 
# Function to convert audio to mono and adjust sample rate
def process_audio(wav_data, target_sample_rate=16000):
    with io.BytesIO(wav_data) as byte_io:
        with wave.open(byte_io, 'rb') as wf:
            params = wf.getparams()
            num_channels = params.nchannels
            sample_rate = params.framerate
 
            # Read frames
            frames = wf.readframes(params.nframes)
            audio_data = np.frombuffer(frames, dtype=np.int16)
           
            # Convert to mono
            if num_channels == 2:
                audio_data = np.mean(audio_data.reshape(-1, 2), axis=1)
 
            # Resample if needed
            if sample_rate != target_sample_rate:
                # Resampling is needed
                import scipy.signal
                number_of_samples = round(len(audio_data) * float(target_sample_rate) / sample_rate)
                resampled_audio_data = scipy.signal.resample(audio_data, number_of_samples)
                audio_data = resampled_audio_data.astype(np.int16)
                sample_rate = target_sample_rate
 
            # Write to a new WAV file
            with io.BytesIO() as processed_byte_io:
                with wave.open(processed_byte_io, 'wb') as processed_wf:
                    processed_wf.setnchannels(1)  # Mono
                    processed_wf.setsampwidth(wf.getsampwidth())
                    processed_wf.setframerate(sample_rate)
                    processed_wf.writeframes(audio_data.tobytes())
               
                return processed_byte_io.getvalue(), sample_rate
 
# Function to transcribe audio using Google Cloud Speech-to-Text
def transcribe_audio(file_content):
    client = speech.SpeechClient()
 
    # Process audio
    processed_audio, sample_rate = process_audio(file_content)
 
    audio = speech.RecognitionAudio(content=processed_audio)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate,
        language_code="en-US",
    )
 
    response = client.recognize(config=config, audio=audio)
    transcription = ' '.join(result.alternatives[0].transcript for result in response.results)
    return transcription
 
# Function to convert text to speech using GTTS
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    with io.BytesIO() as audio_file:
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        audio_data = audio_file.read()
        # Encode audio file content to base64 for playback
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        return audio_base64
 
# Streamlit app
def audiorec_demo_app():
    st.title('Streamlit Audio Recorder')
    st.markdown('Implemented by '
                '[Stefan Rummer](https://www.linkedin.com/in/stefanrmmr/) - '
                'view project source code on '
                '[GitHub](https://github.com/stefanrmmr/streamlit-audio-recorder)')
    st.write('\n\n')
 
    wav_audio_data = st_audiorec()  # Recording audio data
 
    if wav_audio_data is not None:
        # Display audio data as received on the Python side
        st.audio(wav_audio_data, format='audio/wav')
 
        # Transcribe audio
        transcription = transcribe_audio(wav_audio_data)
        st.write(f"Transcription: {transcription}")
 
        # Convert transcription to speech
        audio_base64 = text_to_speech(transcription)
 
        # Embed the synthesized speech in an audio tag and use JavaScript to play it
        st.markdown(
            f'''
            <audio id="tts_audio" src="data:audio/mp3;base64,{audio_base64}" autoplay></audio>
            <script>
                document.getElementById('tts_audio').play();
            </script>
            ''',
            unsafe_allow_html=True
        )
 
if __name__ == '__main__':
    audiorec_demo_app()
 
has context menu
