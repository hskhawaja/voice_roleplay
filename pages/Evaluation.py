import streamlit as st
import numpy as np
from openai_handler import evaluate_conversation

# Set page config
st.set_page_config(
    page_title="Voice Role-Play Trainer",
    page_icon="🎤",
    initial_sidebar_state="expanded",
    layout="wide"
)

# === Custom Styling ===
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0D47A1;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .card {
        background-color: #F4F6F8;
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 1.2rem;
    }

    .sidebar-title {
        text-align: center;
        font-size: 1.6rem;
        color: #1565C0;
        padding-bottom: 1rem;
        border-bottom: 1px solid #ccc;
    }

    .star-score {
        font-size: 20px;
    }

    .feedback-box {
        background-color: #E3F2FD;
        padding: 1.2rem;
        border-radius: 10px;
        font-style: italic;
        box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

def get_score_label(score):
    if score == 10:
        return "Outstanding!"
    elif score >= 9:
        return "Excellent Job!"
    elif score >= 8:
        return "Strong Effort!"
    elif score >= 7:
        return "Very Good!"
    elif score >= 6:
        return "Good!"
    elif score >= 5:
        return "Average"
    elif score >= 4:
        return "Below Average"
    elif score >= 3:
        return "Okay"
    elif score >= 2:
        return "Incomplete"
    else:
        return "Needs Work"

# === Sidebar ===
with st.sidebar:
    st.markdown('<h1 class="sidebar-title">Voice Role-Play Trainer</h1>', unsafe_allow_html=True)
    st.image("https://img.icons8.com/fluency/96/000000/microphone.png", width=80)
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This AI-powered voice role-play trainer simulates real-life seller scenarios to help sales agents sharpen their communication skills.

    Just pick a scenario to begin a conversation.
    """)

# === Main Content ===
st.markdown('<h1 class="main-header">📋 Agent Evaluation Scorecard</h1>', unsafe_allow_html=True)

@st.cache_data(show_spinner=True)
def get_evaluation_result(conversation):
    return evaluate_conversation(conversation)

conversation = st.session_state.get("conversation", [])

if not conversation:
    st.warning("No conversation found. Please interact with the assistant first.")
else:
    evaluation_result = get_evaluation_result(conversation)
    evaluation_scores = evaluation_result.get("scores", {})
    feedback = evaluation_result.get("feedback", "")

    st.subheader("🌟 Evaluation Results")

    for idx, (criterion, score) in enumerate(evaluation_scores.items(), start=1):
        stars = "⭐" * int(score) + "☆" * (5 - int(score))
        with st.container():
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between;">
                    <div><strong>{idx}. {criterion}</strong></div>
                    <div class="star-score">{stars}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    average_score = np.mean(list(evaluation_scores.values()))
    st.divider()
    
    score_label = get_score_label(average_score)
    st.subheader(f"🎯 Average Score: {average_score:.2f} / 10.00 - {score_label}")

    # Construct the feedback box content
    feedback_box = """
    <div class="feedback-box">
        <h4>✅ Performance Review:</h4>
        <h6>What You Did Well:</h6>
        <ul>
    """

    for item in feedback["What You Did Well"]:
        feedback_box += f"<li>{item}</li>"

    feedback_box += """
        </ul>
        <h6>Opportunities to Improve:</h6>
        <ul>
    """

    for item in feedback["Opportunities to Improve"]:
        feedback_box += f"<li>{item}</li>"
   
    feedback_box += f"""
        </ul>
        <h6>Power Line to Practice:</h6>
        "{feedback["Power Line to Practice"]}"
    """

    feedback_box += "<br/><br/>"

    feedback_box += f"""
        {feedback["Additional Feedback"]}
    """
    
    feedback_box += "</div>"

    # Render everything in a single markdown call
    st.markdown(feedback_box, unsafe_allow_html=True)
