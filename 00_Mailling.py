import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- 1. YOUR EMAIL SERVER SETTINGS ---
# If using Gmail:
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 # Port for TLS (Secure connection)

# Pull credentials from GitHub Secrets (NEVER hardcode passwords in your script!)
SENDER_EMAIL = os.environ.get("SMTP_EMAIL")       # e.g., "your.email@gmail.com"
SENDER_PASSWORD = os.environ.get("SMTP_PASSWORD") # The 16-character App Password

def send_newsletter(client_email, subject, html_content):
    """
    Logs into the SMTP server and sends an HTML email to the client.
    """
    # 2. Create the email message container
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Alerte Appels d'Offres <{SENDER_EMAIL}>"
    msg["To"] = client_email

    # 3. Attach the HTML design to the email
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)

    try:
        # 4. Connect to the server and send
        print(f"🔄 Connecting to {SMTP_SERVER}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() # Secure the connection
        
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, client_email, msg.as_string())
        
        print(f"✅ Email successfully sent to {client_email}")
        server.quit()
        
    except Exception as e:
        print(f"❌ Failed to send email to {client_email}. Error: {e}")

# --- HOW TO USE IT IN YOUR MAIN SCRIPT ---
if __name__ == "__main__":
    # Example of how you will call this function inside your main loop
    
    target_client = "ceo.ifcar@example.com"
    email_subject = "🎯 Vos Appels d'Offres - BTP & Consulting (20 Avril 2026)"
    
    # This is the HTML you generated dynamically based on their tags
    email_body = """
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #0056b3;">Alerte Appels d'Offres 🇲🇦</h2>
        <div style="border-left: 4px solid #28a745; padding-left: 10px; background: #f9f9f9; padding: 10px;">
            <h3>Travaux de construction du siège</h3>
            <p><strong>Budget:</strong> 5 000 000 DH</p>
            <p><strong>Date Limite:</strong> 15 Mai 2026</p>
            <a href="http://marchespublics.gov.ma">Voir l'appel d'offres</a>
        </div>
      </body>
    </html>
    """
    
    # Send it!
    send_newsletter(target_client, email_subject, email_body)
