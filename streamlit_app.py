import streamlit as st
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from email_validator import validate_email, EmailNotValidError
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("email")

# Load credentials from Streamlit's secrets
API_KEY = st.secrets["BREVO_API_KEY"]
SENDER_EMAIL = st.secrets["BREVO_SENDER_EMAIL"]
SENDER_NAME = st.secrets["BREVO_SENDER_NAME"]

# Set the Brevo API key
sib_api_v3_sdk.configuration.api_key['api-key'] = API_KEY
api_instance = sib_api_v3_sdk.EmailCampaignsApi()

# Streamlit App UI
st.title("Bulk Email Campaign via Brevo API")
st.write("Create and send bulk email campaigns using Brevo's API.")

# Upload CSV file with email data
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(df)

    # Email details
    email_col = st.selectbox("Select email column", df.columns)
    name_col = st.selectbox("Select name column", df.columns)
    subject = st.text_input("Email Subject", "Your Sales Proposal")
    content = st.text_area("Email Content", "Congratulations! You successfully sent this example campaign via the Brevo API.")

    # Create campaign and send emails when button is clicked
    if st.button("Create and Send Campaign"):
        try:
            # Create the Brevo campaign
            email_campaign = sib_api_v3_sdk.CreateEmailCampaign(
                name="Bulk Campaign via Brevo API",  # Campaign name
                subject=subject,  # Campaign subject
                sender={"name": SENDER_NAME, "email": SENDER_EMAIL},  # Sender info
                type="classic",  # Type of campaign (classic, A/B test, etc.)
                html_content=content,  # Email content
                recipients={"listIds": [1]},  # Replace with your actual list IDs in Brevo
            )

            # Create the email campaign using the Brevo API
            api_response = api_instance.create_email_campaign(email_campaign)
            st.write(f"Campaign created successfully: {api_response}")

            # Log and send the campaign
            for index, row in df.iterrows():
                recipient = row[email_col]
                try:
                    validate_email(recipient)
                    st.write(f"Sending email to {recipient}...")

                    # Add recipients directly (if not using a predefined list)
                    email_data = {
                        "sender": {"email": SENDER_EMAIL},
                        "to": [{"email": recipient}],
                        "subject": subject,
                        "htmlContent": content,
                    }
                    # Send email via Brevo's API (send to one recipient here, but can extend to many)
                    api_instance.send_transac_email(email_data)
                    logger.debug(f"Email sent to {recipient}")
                    st.success(f"Email sent to {recipient}")
                except EmailNotValidError as e:
                    st.error(f"Invalid email: {recipient} - {e}")
                except ApiException as e:
                    st.error(f"Error while sending email to {recipient}: {e}")

        except ApiException as e:
            st.error(f"Exception when calling Brevo API: {e}")
            logger.error(f"Exception when calling Brevo API: {e}")
