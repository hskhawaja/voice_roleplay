# 🎙️ Voice Chat Assistant

A conversational AI web app with voice input and text output, enabling natural back-and-forth conversation powered by **OpenAI** and **ElevenLabs**.

Built with **Streamlit**, this assistant allows users to select a scenario, establish a call, and interact with the AI through voice conversation — offering a seamless, voice-enabled chat experience.

---

## 🚀 Features
- 🎤 **Voice Input**: Click the *Start a Call* button on the call widget.
- ✍️ **Transcription**: Converts your speech to text using Elevenlabs.
- 💬 **OpenAI Response**: Smart replies generated using OpenAI's GPT model through Elevenlabs API.
- 🔊 **Text-to-Speech (TTS)**: AI responses are converted into natural voice using ElevenLabs API.
- 💡 **Chat Interface**: Streamlit-based interface with conversation history and playback.

---

## 🛠️ Tech Stack
Following technologies have been used to build this application.
- 🧠 **OpenAI GPT**: LLM responses
- 🔈 **ElevenLabs**: Text-to-speech (TTS) & Speech-to-text (STT)
- 🌐 **Streamlit**: UI/frontend

## 📦 Installation
### 1. Clone the Repo
```
git clone https://github.com/aminajavaid30/voice-chat.git
cd voice-chat
```

### 2. Install Requirements
It's recommended to use a virtual environment:
```sh
pip install -r requirements.txt
```

### 3. Environment Variables
Create a .env file with the following keys:
```sh
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
AGENT_ID=your_agent_id
```

---

## 📂 Folder Structure
```
voice-chat/                      # Main project folder
│── Home.py                      # Streamlit application
│
│── pages/                       # Pages directory for navigation
│   ├── Evaluation.py            # Evaluation score card
│
│── audio_handler.py             # Audio Handler
│── openai_handler.py            # OpenAI Response Handler
│── elevanlabs_handler.py        # Elevenlabs Handler
│── requirements.txt             # Dependencies
│── .env                         # Environment variables
│── README.md                    # Project documentation
```

---

## ▶️ Run the App
```sh
streamlit run Home.py
```
The app will open in your browser. Select a scenarion, start a call, interact with the agent just like a phone call!
