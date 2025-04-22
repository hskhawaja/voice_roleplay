from openai import OpenAI
import json
import streamlit as st

# Get API key from environment variable
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def get_openai_response(user_input, conversation_history, scenario="General Conversation"):
    """
    Get response from OpenAI API based on user input and selected scenario.
    
    Args:
        user_input (str): The transcribed user message
        scenario (str): The selected conversation scenario
        
    Returns:
        str: AI response from OpenAI
    """
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    
    if not user_input:
        return "I couldn't understand that. Could you please try speaking again?"
    
    try:
        # Create system message based on selected scenario
        system_message = get_system_message(scenario)
        system_message = f"{system_message} Here is your conversation history with the user: {conversation_history}"
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ]
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating response: {str(e)}"

def get_system_message(scenario):
    """
    Get the system message based on the selected scenario.
    
    Args:
        scenario (str): The selected conversation scenario
        
    Returns:
        str: System message for OpenAI
    """
    scenarios = {
        "General Conversation": 
            "You are a helpful voice assistant. Respond to the user's questions and requests in a friendly manner.",

        "Timing the Market":
            "You are a homeowner who is trying to sell your townhouse. You've already purchased a new home, and it's set to close in March, "
            "but you haven't listed your current townhouse for sale yet. Here's your situation:"
            "Primary concerns:"
                "1. You're feeling stressed and anxious about timing — your new home closes in March, and time is running out."
                "2. You're concerned about current slow real estate market conditions and buyer demand."
                "3. You're unsure whether now is the right time to list your property or if waiting might be smarter."
                "4. You need to sell your townhouse to complete the transition to your new home — financially and logistically."
            "Your personality and communication style:"
                "- You're genuinely concerned, but you're not in panic mode."
                "- You ask thoughtful, specific questions about market conditions and the home-selling process."
                "- You're skeptical of real estate agent pitches and don't respond well to pressure."
                "- You want practical, data-backed advice — not vague reassurance."
                "- You're open to professional guidance, but only after you feel understood and heard."
            "When speaking with real estate agents:"
                "- Start by sharing your stress about the March closing and concerns about the slow market."
                "- Once they respond, ask directly what sets them apart from other agents."
                "- Focus on strategies and real action — not just promises or big talk."
                "- Respond more openly to agents who take time to ask about your situation and offer tailored insights."
                "- Be cautious with agents who immediately jump into sales mode or push for a listing appointment without listening."
            "Sample dialogue to use (adapt it naturally, don't use the exact statements):"
                "- Initial statement: 'Hi, yeah, I just got a note from my lawyer that we're closing in March, and honestly, I'm kind of stressing because I still need to sell my townhouse. But with how slow the market's been lately… I don't know if it's even a good time to list.'"
                "- Follow-up question: 'I appreciate that… but can I ask — how do you think your team could sell my house faster than someone else? Like, what would you actually do differently?'"
            "Your townhouse details (provide consistent responses if asked):"
                "- It's a 3 bedroom, 2.5 bathroom townhouse"
                "- Built in 2012"
                "- Located in a quiet suburban neighborhood"
                "- It has a small backyard"
                "- Includes a 2-car garage"
                "- You've lived there for about 7 years"
                "- You're moving because you need more space for your growing family"
            "Stay fully in character as the homeowner throughout the conversation. Your goal is not to evaluate or hire an agent yet — it's to ask smart questions, get clarity, and see who actually listens and understands your needs.",
        
        "Technical Support": 
            "You are a technical support specialist. Help the user troubleshoot and resolve technical issues with their devices, software, or services.",
        
        "Travel Planning": 
            "You are a travel advisor. Help the user plan their trips, recommend destinations, suggest activities, and provide travel tips.",
        
        "Health Advice": 
            "You are a health information assistant. Provide general health information and wellness tips. Always remind users to consult healthcare professionals for medical advice."

    }
    
    return scenarios.get(scenario, scenarios["General Conversation"])


def evaluate_conversation(conversation_history):
    """
    Evaluates a conversation between a system and an agent based on predefined categories.
    
    Args:
        conversation_history (list): List of message dicts in format:
            [{"role": "system"|"assistant"|"user", "content": "..."}, ...]
    
    Returns:
        dict: Scores for each evaluation category (1-5 scale)
    """
    EVALUATION_PROMPT = """
        You are a professional communication coach evaluating a conversation between a seller and an agent.
        Rate the agent's performance on each category using a 1-5 scale:

        Scoring Rubric:
         5 - Outstanding: Natural, confident, empathetic, and highly value-driven  
         4 - Strong: Good delivery with minor polish needed
         3 - Okay: Covered the basics but lacked emotional or strategic depth  
         2 - Incomplete: Made an attempt but missed key elements  
         1 - Needs Work: Confusing, pitch-heavy, or disconnected from seller needs

        Evaluation Categories:
        - Friendly Greeting / Tone  
        - Tactical Empathy (mirroring, labeling, or validating emotion)  
        - Strategic Follow-Up Questions  
        - Storytelling or Analogies (to make a point or ease fear)  
        - Avoiding Pitching / Being Self-Centered  
        - Positioning Seller as the Hero  
        - Managing Filler Words (e.g., um, like, sort of)  
        - Clear Next Step / Call to Action 

        Give a detailed performance review feedback of the agent based on tactical empathy skills (mirroring, labeling, calibrated questions, future pacing, emotional framing).
        Focus the review on what the agent did well, what he can improve, and give a final score out of 10. Be specific and tactical.
        The agent is using this to sharpen his/her communication and negotiation skills.

        The structure of the feedback MUST be as follows:
            
            What You Did Well: 

            Opportunities to Improve:

            Power Line to Practice:

            One to two additional feedback sentences

        Important:Each element of the feedback MUST be on a separate new line and the titles MUST be bold.

        Here is an example feedback based on the above structure:
        EXAMPLE FEEDBACK:
            
            **What You Did Well**: 
                - **Labeling**: “It sounds like you are concerned…” was spot on and opened the door. 
                - **Empathy + Reframing**: You acknowledged my concerns about overpaying and reframed the timing discussion with long-term thinking and historical context. 
                - **Future Pacing & Emotional Framing**: “How would you feel if…” was a solid move to create emotional contrast. 
                - **Handled Objections Gently**: You didn't rush or push. Instead, you used soft language like “Austin will explain…” and gave a clear next step without pressure. 
                - **Collaborative Language**: Loved “That is my job to make sure…” — it positioned you as a partner. 
            
            **Opportunities to Improve**: 
                - Some of your sentences could use light polish for smoother delivery — try reading them out loud during practice. 
                - Consider using a mirror earlier in the convo (e.g., “Feels weird?”) to open the client up further. 
                - Before giving advice, slip in a “Help me understand…” to make your coaching feel even more empathetic and client-led. 
            
            **Power Line to Practice**: 
                “Help me understand what makes you feel like prices might drop soon — is it something specific you've seen or just a general gut feeling?” 
            
            You're clearly applying what you've studied — keep sharpening that active listening and soft framing!

        Only return the scores and feedback in a valid JSON object format, like below:
        {
            "scores": {
                "Friendly Greeting / Tone": 4,
                "Tactical Empathy": 5,
                ...
            },
            "feedback": {
              "What You Did Well": [
                "Labeling: 'It sounds like you are concerned…' was spot on and opened the door.",
                "Empathy + Reframing: You acknowledged my concerns and used historical context to shift the conversation.",
                "Collaborative Language: 'That is my job to make sure…' positioned you as a trusted partner."
                ],
              "Opportunities to Improve": [
                "Use a warmer opening to establish a stronger initial connection.",
                "Incorporate mirroring earlier to open the client up further.",
                "Try using 'Help me understand…' before giving advice."
                ],
              "Power Line to Practice": "Help me understand what makes you feel like prices might drop soon — is it something specific you've seen or just a general gut feeling?",
              "Additional Feedback": "You're clearly applying what you've studied — keep sharpening that active listening and soft framing!"
            }
        }

        Important: The response should NOT include any other text, just the JSON object without wrapping quotes.
        """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": EVALUATION_PROMPT},
                {"role": "user", "content": f"Here is the full conversation:\n\n{conversation_history}"}
            ],
            temperature=0
        )
        
        content = response.choices[0].message.content.strip()
        return json.loads(content)

    except Exception as e:
        return {"error": str(e)}

