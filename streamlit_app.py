import streamlit as st
import google.generativeai as genai
import pandas as pd
import sib_api_v3_sdk
from email_validator import validate_email, EmailNotValidError
import datetime
import logging
from pprint import pprint

# Configure the API key securely from Streamlit's secrets for Google AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Set up the API key for Brevo using the correct method
api_key = st.secrets["BREVO_API_KEY"]
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = api_key
api_instance = sib_api_v3_sdk.EmailCampaignsApi(sib_api_v3_sdk.ApiClient(configuration))

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("email")

# Function to create and send email campaign using Brevo
def send_email_via_brevo(recipient, subject, body):
    # Define the email campaign settings
    email_campaigns = sib_api_v3_sdk.CreateEmailCampaign(
        name="Sales Proposal Campaign",
        subject=subject,
        sender={"name": "Your Company", "email": st.secrets["BREVO_EMAIL"]},
        type="classic",
        html_content=body,
        recipients={"emails": [recipient]},
        scheduled_at=None  # Send immediately, or you can set a schedule here
    )

    try:
        api_response = api_instance.create_email_campaign(email_campaigns)
        logger.debug(f"Email campaign created: {api_response}")
        return True
    except sib_api_v3_sdk.rest.ApiException as e:
        logger.error(f"Exception when creating email campaign: {e}")
        st.error(f"Error: {e}")
        return False

# Function to generate sales proposal
def generate_proposal(data, template):
    prompt = f"Generate a sales proposal based on the following data: {data.to_dict()} and using the template: {template}"
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# Function to log proposals
def log_proposal(recipient, proposal):
    with open("proposal_log.txt", "a") as file:
        file.write(f"Recipient: {recipient}\n")
        file.write(f"Proposal: {proposal}\n")
        file.write(f"Date: {datetime.datetime.now()}\n")
        file.write("-" * 50 + "\n")

# Streamlit App UI
st.title("Sales Proposal Generator")
st.write("Generate and send personalized sales proposals using Generative AI.")

# Confirm that secrets are loaded
st.write("GOOGLE_API_KEY:", st.secrets["GOOGLE_API_KEY"])
st.write("BREVO_API_KEY:", st.secrets["BREVO_API_KEY"])
st.write("BREVO_EMAIL:", st.secrets["BREVO_EMAIL"])

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(df)

    # Email details
    email_col = st.selectbox("Select email column", df.columns)
    subject = st.text_input("Email Subject", "Your Sales Proposal")
    template = st.text_area("Proposal Template", "Dear [Name],\n\nWe are pleased to present our sales proposal...\n\nBest regards,\n[Company Name]")

    if st.button("Generate and Send Proposals"):
        for index, row in df.iterrows():
            recipient = row[email_col]
            try:
                validate_email(recipient)
                proposal = generate_proposal(row, template)
                st.write(f"Preview of Proposal for {recipient}:")
                st.write(proposal)

                # Send email using Brevo API
                if send_email_via_brevo(recipient, subject, proposal):
                    log_proposal(recipient, proposal)
                    st.success(f"Proposal sent to {recipient} successfully!")
                else:
                    st.error(f"Failed to send proposal to {recipient}")
            except EmailNotValidError as e:
                st.error(f"Invalid email: {recipient} - {e}")

if st.button("View Proposal Log"):
    try:
        with open("proposal_log.txt", "r") as file:
            st.text(file.read())
    except FileNotFoundError:
        st.write("No proposals have been logged yet.")
