from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
import streamlit as st

AGENT_ID = st.secrets["AGENT_ID"]
API_KEY = st.secrets["ELEVENLABS_API_KEY"]

def get_latest_conversation():
    """
    Retrieves the latest conversation for the selected agent from the ElevenLabs API.
    
    Returns:
    list: The latest conversation for the selected agent.
    """
    
    if not AGENT_ID:
       print("AGENT_ID environment variable must be set\n")
    
    if not API_KEY:
       print("ELEVENLABS_API_KEY not set, assuming the agent is public\n")

    try:
        client = ElevenLabs(api_key=API_KEY)

        conversations = client.conversational_ai.get_conversations(agent_id=AGENT_ID)
        # get latest conversation
        latest_conversation_id = conversations.conversations[0].conversation_id

        latest_conversation = client.conversational_ai.get_conversation(
                                conversation_id=latest_conversation_id,
                            )
    except Exception as e:
        print(f"Error getting latest conversation: {e}")

    return latest_conversation