"""
Test script to verify SendGrid email configuration.

This script sends a simple test email to confirm that your SendGrid
API key and sender authentication are correctly configured.
"""

import os
from dotenv import load_dotenv
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content


def send_test_email():
    """Send a test email to verify SendGrid configuration."""
    
    # Load environment variables
    load_dotenv(override=True)
    
    # Get configuration from environment
    api_key = os.environ.get('SENDGRID_API_KEY')
    sender_email = os.environ.get('SENDER_EMAIL')
    recipient_email = os.environ.get('RECIPIENT_EMAIL')
    
    # Validate configuration
    if not api_key:
        print("❌ Error: SENDGRID_API_KEY not found in .env file")
        return False
    
    if not sender_email:
        print("❌ Error: SENDER_EMAIL not found in .env file")
        return False
        
    if not recipient_email:
        print("❌ Error: RECIPIENT_EMAIL not found in .env file")
        return False
    
    try:
        # Initialize SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        
        # Create email
        from_email = Email(sender_email)
        to_email = To(recipient_email)
        subject = "Test Email - Deep Research Agent"
        content = Content(
            "text/plain", 
            "This is a test email to verify your SendGrid configuration for the Deep Research Agent."
        )
        
        mail = Mail(from_email, to_email, subject, content).get()
        
        # Send email
        response = sg.client.mail.send.post(request_body=mail)
        
        # Check response
        if response.status_code == 202:
            print("✅ Success! Test email sent successfully.")
            print(f"   Status Code: {response.status_code}")
            print(f"   From: {sender_email}")
            print(f"   To: {recipient_email}")
            print("\nℹ️  Check your email inbox (and spam folder) for the test message.")
            return True
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your SENDGRID_API_KEY is correct")
        print("2. Confirm your sender email is verified in SendGrid")
        print("3. Check SendGrid dashboard for more details")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("SendGrid Email Configuration Test - Deep Research Agent")
    print("=" * 60)
    print()
    send_test_email()
    print()
    print("=" * 60)
