import os
import tempfile
import pyaudio
import wave
import uuid
import time
import threading
from faster_whisper import WhisperModel
from elevenlabs.client import ElevenLabs
import streamlit as st
import base64

def load_model():
    try:
        model = WhisperModel("small", device="cpu", compute_type="int8")
        return model
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        return None
    
def load_ElevenLabs_client():
    try:
        client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        return client
    except Exception as e:
        print(f"Error loading ElevenLabs client: {e}")
        return None

def record_audio(duration=None, sample_rate=16000, start_only=False, stop_recording=None):
    """
    Record audio using the microphone.
    
    Args:
        duration (int, optional): Duration in seconds to record. If None, records until stopped.
        sample_rate (int): Sample rate for the audio recording.
        start_only (bool): If True, only starts recording and returns the recorder object.
        stop_recording (object): Recorder object to stop recording and save audio.
        
    Returns:
        str: Path to the recorded audio file or recorder object if start_only=True.
    """
    global frames, is_recording, stop_recording_event
    
    if stop_recording is not None:
        # We're stopping an existing recording
        stop_recording_event.set()  # Signal the recording thread to stop
        time.sleep(0.5)  # Give it a moment to finish
        
        # Save the recorded audio to a file
        temp_dir = tempfile.gettempdir()
        audio_file = os.path.join(temp_dir, f"recording_{uuid.uuid4()}.wav")
        
        wf = wave.open(audio_file, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Reset the global variables
        frames = []
        is_recording = False
        stop_recording_event = None
        
        return audio_file
    
    if start_only:
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Reset globals
        frames = []
        is_recording = True
        stop_recording_event = threading.Event()
        
        # Open stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        # Start recording in a separate thread
        def record_thread():
            global frames, is_recording
            while is_recording and not stop_recording_event.is_set():
                data = stream.read(1024)
                frames.append(data)
            
            # Close and terminate when done
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        # Start the recording thread
        threading.Thread(target=record_thread).start()
        
        # Return a recorder object (in this case, just a dummy object as identifier)
        return "recorder_active"
    
    # If we're here, it's the original fixed-duration recording method
    # This is kept for backward compatibility but shouldn't be used in the new implementation
    p = pyaudio.PyAudio()
    
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=1024
    )
    
    print("* Recording audio...")
    
    frames = []
    for i in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    
    print("* Recording complete.")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save the recorded audio to a file
    temp_dir = tempfile.gettempdir()
    audio_file = os.path.join(temp_dir, f"recording_{uuid.uuid4()}.wav")
    
    wf = wave.open(audio_file, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return audio_file

def transcribe_audio(audio_file):
    """
    Transcribe the audio file using faster-whisper.
    
    Returns:
        str: Transcribed text or error/fallback message.
    """
    if not audio_file or not os.path.exists(audio_file):
        return "Sorry, I couldn't capture any audio."

    # Handle fallback text file (demo mode)
    if audio_file.endswith(".txt"):
        try:
            with open(audio_file, "r") as file:
                return file.read() + " (Demo mode - microphone not available)"
        except Exception as e:
            print(f"Error reading fallback text file: {e}")
            return "Unable to read the fallback file. Microphone may be unavailable."

    model = load_model()
    if not model:
        return "Model failed to load. Please check system resources or model path."

    try:
        print("Model loaded successfully. Transcribing audio...")
        segments, _ = model.transcribe(audio_file)
        full_text = " ".join(segment.text for segment in segments)
        return full_text.strip() if full_text else "I couldn't understand the audio. Please try again."

    except Exception as e:
        print(f"Error transcribing audio with faster-whisper: {e}")
        return "I'm having trouble transcribing your audio. Please try again or speak more clearly."

    finally:
        # Clean up the audio file
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
        except Exception as cleanup_err:
            print(f"Failed to remove temporary file: {cleanup_err}")

def play_audio(message):
    """
    Play the audio message using ElevenLabs and increase its volume.
    
    Args:
        message (str): The message to be played.
        
    Returns:
        str: A message indicating the status of the audio playback.
    """
    elevenlabs_client = load_ElevenLabs_client()
    if not elevenlabs_client:
        return "ElevenLabs client failed to load."

    try:
        print("Client loaded successfully. Generating speech...")

        # audio is now a generator, so we must join all chunks into bytes
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=message,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        audio_bytes = b"".join(audio_generator)

        b64_audio = base64.b64encode(audio_bytes).decode()
        audio_tag = f"""
            <audio id="hidden-audio" autoplay hidden>
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            </audio>
            <script>
                const audio = document.getElementById("hidden-audio");
                audio.onended = () => {{
                    const url = new URL(window.location.href);
                    url.searchParams.set('__playback_done', '1');
                    window.location.href = url.toString();
                }};
            </script>
        """
        st.markdown(audio_tag, unsafe_allow_html=True)
        # Show a message while audio plays
        st.info("🔊 Playing audio... Please wait.")
    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return "I'm having trouble generating speech. Please try again."