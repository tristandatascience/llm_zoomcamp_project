import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Page configuration
st.set_page_config(page_title="LLM ChatBot", page_icon="🤖", layout="wide")

# FastAPI backend URL
backend_url = "http://backend:9000"

# File to store feedback
FEEDBACK_FILE = "user_feedback.csv"

# Custom CSS for chat style
st.markdown("""
<style>
    .chat-container {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #2B5B84;
        color: white;
        border-radius: 20px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 75%;
        float: right;
        clear: both;
    }
    .bot-message {
        background-color: #383838;
        color: white;
        border-radius: 20px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 75%;
        float: left;
        clear: both;
    }
    .clear {
        clear: both;
    }
    .feedback-form {
        background-color: #2E2E2E;
        border-radius: 10px;
        padding: 10px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Feedback functions
def save_feedback(query, response, rating, comment):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedback_data = pd.DataFrame({
        "timestamp": [timestamp],
        "query": [query],
        "response": [response],
        "rating": [rating],
        "comment": [comment]
    })
    
    if os.path.exists(FEEDBACK_FILE):
        existing_data = pd.read_csv(FEEDBACK_FILE)
        updated_data = pd.concat([existing_data, feedback_data], ignore_index=True)
    else:
        updated_data = feedback_data
    
    updated_data.to_csv(FEEDBACK_FILE, index=False)

def show_feedback_form(query, response, index):
    with st.expander(f"Give feedback for response {index}"):
        rating = st.slider(f"How would you rate this response? (Response {index})", 1, 5, 3, key=f"rating_{index}")
        comment = st.text_area("Additional comments (optional)", key=f"comment_{index}")
        
        if st.button("Submit feedback", key=f"submit_{index}"):
            save_feedback(query, response, rating, comment)
            st.success("Thank you for your feedback!")

def create_feedback_charts(data):
    st.subheader("Feedback Dashboard")

    # 1. Rating Distribution
    fig_rating = px.histogram(data, x="rating", nbins=5, title="Rating Distribution")
    fig_rating.update_layout(xaxis_title="Rating", yaxis_title="Count")
    st.plotly_chart(fig_rating)

    # 2. Average Rating Over Time
    data['date'] = pd.to_datetime(data['timestamp']).dt.date
    avg_rating = data.groupby('date')['rating'].mean().reset_index()
    fig_avg = px.line(avg_rating, x="date", y="rating", title="Average Rating Over Time")
    fig_avg.update_layout(xaxis_title="Date", yaxis_title="Average Rating")
    st.plotly_chart(fig_avg)

    # 3. Feedback Volume Over Time
    feedback_volume = data.groupby('date').size().reset_index(name='count')
    fig_volume = px.bar(feedback_volume, x="date", y="count", title="Feedback Volume Over Time")
    fig_volume.update_layout(xaxis_title="Date", yaxis_title="Number of Feedbacks")
    st.plotly_chart(fig_volume)

    # 4. Top 10 Most Common Words in Comments
    from collections import Counter
    import re

    def get_top_words(text, n=10):
        words = re.findall(r'\w+', text.lower())
        return Counter(words).most_common(n)

    all_comments = ' '.join(data['comment'].dropna())
    top_words = get_top_words(all_comments)
    word_df = pd.DataFrame(top_words, columns=['word', 'count'])
    fig_words = px.bar(word_df, x="word", y="count", title="Top 10 Most Common Words in Comments")
    fig_words.update_layout(xaxis_title="Word", yaxis_title="Count")
    st.plotly_chart(fig_words)

    # 5. Rating Distribution by Day of Week
    data['day_of_week'] = pd.to_datetime(data['timestamp']).dt.day_name()
    fig_dow = px.box(data, x="day_of_week", y="rating", title="Rating Distribution by Day of Week")
    fig_dow.update_layout(xaxis_title="Day of Week", yaxis_title="Rating")
    st.plotly_chart(fig_dow)

def show_feedback_statistics():
    if os.path.exists(FEEDBACK_FILE):
        data = pd.read_csv(FEEDBACK_FILE)
        st.subheader("Feedback Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Feedbacks", len(data))
        with col2:
            st.metric("Average Rating", f"{data['rating'].mean():.2f}")
        with col3:
            st.metric("Median Rating", f"{data['rating'].median():.1f}")
        
        create_feedback_charts(data)
        
        st.subheader("Recent Comments")
        recent_comments = data[['timestamp', 'rating', 'comment']].tail(5)
        st.table(recent_comments)
    else:
        st.info("No feedback has been collected yet.")

# Function to query the backend
def query_backend(user_input):
    response = requests.post(f"{backend_url}/chat?query={user_input}")
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Error querying the backend: {response.status_code}"}

# Create sidebar menu
menu = [ "Set LLM", "Upload PDF", "Chat", "Feedback and Statistics"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Chat":
    # Application title
    st.title("Chat with a PDF 🤖")

    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Chat area
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for index, message in enumerate(st.session_state.chat_history):
        if message['type'] == 'user':
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
            # Add feedback form after each bot response
            if index > 0:  # Ensure there's a previous question
                show_feedback_form(st.session_state.chat_history[index-1]["content"], message["content"], index//2 + 1)
        st.markdown('<div class="clear"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # User input area
    user_input = st.text_input("Ask your question:", key="user_input")

    if st.button("Send"):
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({"type": "user", "content": user_input})
            
            # Loading animation
            with st.spinner('Processing your request...'):
                response_json = query_backend(user_input)
            
            # Add bot response to history
            if "response" in response_json:
                bot_response = response_json["response"]
                st.session_state.chat_history.append({"type": "bot", "content": bot_response})
            elif "error" in response_json:
                st.session_state.chat_history.append({"type": "bot", "content": f"Error: {response_json['error']}"})
            
            # Reload the page to show the new message
            st.rerun()

elif choice == "Upload PDF":
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        files = {"file": uploaded_file}
        with st.spinner('Uploading and indexing PDF...'):
            response = requests.post(f"{backend_url}/upload_pdf", files=files)
        st.success(response.json()["message"])

elif choice == "Feedback and Statistics":
    st.title("Feedback and Statistics")
    show_feedback_statistics()


elif choice == "Set LLM":
    st.title("LLM Settings")
    api_key_ = ''
    # LLM Provider selection
    llm_provider = st.radio(
        "Select LLM provider (llama 3.1:8b for Groq and DeepInfra. Notes: Groq api is free see https://groq.com/) or local LLM with Ollama (local LLM no API/Tokens/Provider needed)",
        ("Ollama llama3.2:1b (Default)","Groq", "DeepInfra")
    )
    st.session_state['llm_provider'] = llm_provider
    if llm_provider != "Ollama llama3.2:1b (Default)":
        api_key_ = st.text_input("Enter API Key", type="password")
        st.session_state['api_key'] = api_key_
    else:
        api_key_ = str("nokey")
    
    if st.button("Save Settings"):
        # Here you would typically save these settings to a configuration file or database
        # For this example, we'll just store them in session state
        llm_provider_str = str(llm_provider)
        response = requests.post(f"{backend_url}/update_llm_settings", 
                                 json={"provider": llm_provider, "api_key": api_key_})
        
        if response.status_code == 200:
            st.success("Settings saved successfully!")
        else:
            st.error("Failed to save settings. Please try again.")
    
    # Display current settings
    st.subheader("Current Settings")
    st.write(f"LLM Provider: {st.session_state.get('llm_provider', 'Not set')}")
    st.write("API Key: ", "*" * len(st.session_state.get('api_key', '')) if 'api_key' in st.session_state else "Not set")
