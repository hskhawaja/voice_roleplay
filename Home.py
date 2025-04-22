import streamlit as st
import os
import streamlit.components.v1 as components
from elevenlabs_handler import get_latest_conversation
from streamlit_autorefresh import st_autorefresh

AGENT_ID = st.secrets["AGENT_ID"]

# Set page config
st.set_page_config(
    page_title="Voice Role-Play Trainer",
    page_icon="🎤",
    initial_sidebar_state="expanded",
    layout="wide"
)

# Inject enhanced UI CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.7rem;
        color: #0D47A1;
        text-align: center;
        margin-bottom: 1.2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .info-box {
        background-color: #E3F2FD;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 2rem auto 1rem auto;
        max-width: 750px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.07);
    }

    .user-bubble, .assistant-bubble {
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        max-width: 80%;
        font-size: 1.05rem;
        line-height: 1.5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        font-family: 'Segoe UI', sans-serif;
    }

    .user-bubble {
        background-color: #F0F9FF;
        align-self: flex-end;
        border-top-right-radius: 0;
    }

    .assistant-bubble {
        background-color: #F9FBE7;
        align-self: flex-start;
        border-top-left-radius: 0;
    }

    .sidebar-title {
        text-align: center;
        font-size: 1.6rem;
        color: #1565C0;
        padding-bottom: 1rem;
        border-bottom: 1px solid #ccc;
    }

    .stButton > button {
        border-radius: 25px;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
        background-color: #1E88E5;
        color: white;
        transition: background-color 0.3s ease;
        margin-bottom: 1rem;
    }

    .stButton > button:hover {
        background-color: #1565C0;
        transform: scale(1.02);
    }

    [data-testid="stSidebarNav"] {
        display: none;
    }

    .element-container:has(.user-bubble), .element-container:has(.assistant-bubble) {
        padding-left: 1rem;
        padding-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
for key, default in {
    "messages": [],
    "conversation": [],
    "recording": False,
    "processing": False,
    "scenario": "Select Scenario",
    "previous_scenario": None,
    "transcription": "",
    "audio_file": None,
    "recorder": None,
    "scenario_selected": False,
    "conversation_started": False,
    "conversation_finished": False,
    "messages_appended": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Scenario intro message
scenario_intros = {
    "Timing the Market": "Hi, yeah, I just got a note from my lawyer that we're closing in March, and honestly, I'm kind of stressing because I still need to sell my townhouse. But with how slow the market's been lately… I don't know if it's even a good time to list."
}

# Sidebar layout
with st.sidebar:
    st.markdown('<h1 class="sidebar-title">Voice Role-Play Trainer</h1>', unsafe_allow_html=True)
    st.image("https://img.icons8.com/fluency/96/000000/microphone.png", width=80)

    st.markdown("### Conversation Settings")
    st.session_state.scenario = st.selectbox(
        "Scenario",
        ["Select Scenario", "Timing the Market"]
    )

    if st.button("Evaluate"):
        st.switch_page("pages/Evaluation.py")

    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This AI-powered voice role-play trainer simulates real-life seller scenarios to help sales agents sharpen their communication skills.

    Just pick a scenario to begin a conversation.
    """)

# Main header
st.markdown('<h1 class="main-header">Voice Role-Play Trainer</h1>', unsafe_allow_html=True)

# First-time instructions
if st.session_state.scenario == "Select Scenario" and not st.session_state.messages:
    st.session_state.scenario_selected = False
    st.markdown("""
    <div class="info-box">
        <h3>👋 Welcome to Voice Chat Assistant!</h3>      
        <p>Select the conversation scenario from the sidebar to begin a conversation.</p>
    </div>
    """, unsafe_allow_html=True)

# Scenario logic
if st.session_state.scenario != "Select Scenario":
    st.session_state.previous_scenario = st.session_state.scenario
    st.session_state.scenario_selected = True

if st.session_state.previous_scenario != "Select Scenario":
    st.session_state.scenario = st.session_state.previous_scenario

# Conversation logic
if st.session_state.scenario_selected:
    intro_msg = scenario_intros.get(st.session_state.scenario, None)

    html_code = f"""
    <div style="position: fixed; bottom: 20px; left: 63%; transform: translateX(-50%); z-index: 9999;">
        <elevenlabs-convai agent-id="{AGENT_ID}"></elevenlabs-convai>
    </div>
    <script src="https://elevenlabs.io/convai-widget/index.js" async type="text/javascript"></script>
    """
    components.html(html_code, height=180)

    if intro_msg:
        st.session_state.conversation = []

    while True:
        latest_conversation = get_latest_conversation()

        if latest_conversation.status == "in-progress":
            st.session_state.conversation_started = True

        if st.session_state.conversation_started and latest_conversation.status == "done":
            st.session_state.conversation_finished = True
            break

# Fix: Avoid appending empty/None messages
if st.session_state.conversation_finished and not st.session_state.messages_appended:
    for item in latest_conversation.transcript:
        if not item.message or item.message.strip() == "":
            continue
        role = "assistant" if item.role == "agent" else "user"
        st.session_state.messages.append({"role": role, "content": item.message})
        st.session_state.conversation.append({
            "role": "system" if role == "assistant" else "user",
            "content": item.message
        })
    st.session_state.messages_appended = True

# Display chat and reset button only after conversation starts
if st.session_state.messages:
    with st.container():
        st.markdown("### 💬 Conversation")

        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.session_state.conversation = []
            st.session_state.conversation_started = False
            st.session_state.conversation_finished = False
            st.session_state.messages_appended = False
            st.session_state.previous_scenario = None
            st.session_state.scenario = "Select Scenario"
            st.session_state.scenario_selected = False
            count = st_autorefresh(interval=2000, limit=1, key="fizzbuzzcounter")

        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-bubble"><strong>👤</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-bubble"><strong>🤖</strong> {message["content"]}</div>', unsafe_allow_html=True)
