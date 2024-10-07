import streamlit as st
import pandas as pd
from datetime import datetime
import os

FEEDBACK_FILE = "user_feedback.csv"

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

def show_feedback_form(query, response):
    st.subheader("Votre avis est important")
    rating = st.slider("Comment évaluez-vous cette réponse ?", 1, 5, 3)
    comment = st.text_area("Commentaires supplémentaires (optionnel)")
    
    if st.button("Soumettre le feedback"):
        save_feedback(query, response, rating, comment)
        st.success("Merci pour votre feedback !")

def show_feedback_statistics():
    if os.path.exists(FEEDBACK_FILE):
        data = pd.read_csv(FEEDBACK_FILE)
        st.subheader("Statistiques de feedback")
        st.write(f"Nombre total de feedbacks : {len(data)}")
        st.write(f"Note moyenne : {data['rating'].mean():.2f}")
        
        st.subheader("Distribution des notes")
        rating_counts = data['rating'].value_counts().sort_index()
        st.bar_chart(rating_counts)
        
        st.subheader("Derniers commentaires")
        recent_comments = data[['timestamp', 'rating', 'comment']].tail(5)
        st.table(recent_comments)
    else:
        st.info("Aucun feedback n'a encore été collecté.")

def run_feedback_page():
    st.title("Feedback et Statistiques")
    show_feedback_statistics()