import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from datetime import datetime
import random

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Dummy user authentication (simple for demo)
admin_password = "admin123"  # Replace with secure password handling in real applications

# Simulated database of feedback
feedback_data = []

# Simulated predefined categories
feedback_categories = ['Workplace Environment', 'Workload', 'Management', 'Career Development', 'Other']

# Store user session for admin login
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Admin Login
def admin_login():
    st.session_state.admin_logged_in = False
    password = st.text_input("Enter Admin Password", type="password")
    if password == admin_password:
        st.session_state.admin_logged_in = True
        st.success("Admin logged in successfully.")
    else:
        st.error("Incorrect password.")

# Feedback Submission Form
def submit_feedback():
    with st.form(key='feedback_form'):
        st.subheader("Submit Your Anonymous Feedback:")
        feedback = st.text_area("Enter your feedback or survey response:")
        category = st.selectbox("Select Feedback Category", feedback_categories)
        submit_button = st.form_submit_button(label="Submit Feedback")

        if submit_button:
            if feedback.strip():
                # Add timestamp and store feedback with category
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                feedback_entry = {"feedback": feedback.strip(), "category": category, "timestamp": timestamp}
                feedback_data.append(feedback_entry)
                st.success("Your feedback has been submitted successfully!")
            else:
                st.warning("Please enter your feedback before submitting.")

# Admin Dashboard for Viewing Feedback
def admin_dashboard():
    if st.session_state.admin_logged_in:
        st.title("Admin Dashboard")
        st.write("View and analyze all feedback submitted by employees.")

        # Feedback View
        st.write("### All Submitted Feedback")
        for idx, entry in enumerate(feedback_data, 1):
            st.write(f"{idx}. {entry['timestamp']} | Category: {entry['category']} - {entry['feedback']}")

        # Option to filter by category, sentiment, or date
        filter_category = st.selectbox("Filter Feedback by Category", ['All'] + feedback_categories)
        if filter_category != 'All':
            filtered_feedback = [entry for entry in feedback_data if entry['category'] == filter_category]
        else:
            filtered_feedback = feedback_data

        # Sentiment Visualization
        sentiment_analysis = [feedback_sentiment_analysis(entry['feedback']) for entry in filtered_feedback]
        sentiment_df = pd.DataFrame(sentiment_analysis, columns=["Feedback", "Sentiment"])

        sentiment_counts = sentiment_df["Sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]

        st.write("### Sentiment Distribution:")
        fig, ax = plt.subplots()
        sns.barplot(data=sentiment_counts, x="Sentiment", y="Count", ax=ax)
        st.pyplot(fig)

        # Export Data as CSV
        if st.button("Export Feedback Data as CSV"):
            df = pd.DataFrame(filtered_feedback)
            df.to_csv("feedback_data.csv", index=False)
            st.success("CSV file exported successfully.")

# Feedback Sentiment Analysis (Basic)
def feedback_sentiment_analysis(feedback_text):
    """
    Simple sentiment analysis function. In real applications, you could use an API like Google Cloud NLP
    or other libraries (e.g., TextBlob, Hugging Face models) for more accurate sentiment classification.
    """
    if "happy" in feedback_text.lower() or "good" in feedback_text.lower():
        return feedback_text, "Positive"
    elif "bad" in feedback_text.lower() or "poor" in feedback_text.lower():
        return feedback_text, "Negative"
    else:
        return feedback_text, "Neutral"

# Main app functionality
def main():
    st.title("Employee Survey & Feedback Analysis")
    st.write("This app collects anonymous feedback from employees and analyzes it using AI.")

    # User role selection (admin or normal user)
    role = st.radio("Select your role", ["Employee", "Admin"])

    # Employee feedback submission
    if role == "Employee":
        submit_feedback()

        # Real-time summary and word cloud
        if len(feedback_data) > 0:
            all_feedback_text = ' '.join([entry['feedback'] for entry in feedback_data])
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_feedback_text)
            st.write("### Word Cloud of Feedback:")
            st.image(wordcloud.to_array(), use_column_width=True)

    # Admin login and dashboard
    elif role == "Admin":
        if st.session_state.admin_logged_in:
            admin_dashboard()
        else:
            admin_login()

# Run the app
if __name__ == "__main__":
    main()
