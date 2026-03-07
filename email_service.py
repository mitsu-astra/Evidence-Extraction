"""
Email Service for KMIT Authentication
Sends credentials to users after signup
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


def send_credentials_email(
    to_email: str,
    uid: str,
    password: str,
    full_name: Optional[str] = None
) -> dict:
    """
    Send UID and password to user's email after signup.
    
    Args:
        to_email: Recipient's email address
        uid: Generated UID
        password: Today's password
        full_name: User's name (optional)
    
    Returns:
        {"success": bool, "message": str}
    """
    
    # Email configuration from environment variables
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return {
            "success": False,
            "message": "Email service not configured. Check SENDER_EMAIL and SENDER_PASSWORD in .env"
        }
    
    # Create email content
    greeting = f"Hello {full_name}," if full_name else "Hello,"
    
    subject = "Forensic Portal - Your Account Credentials"
    
    html_content = f"""
    <html>
        <body style="font-family: 'Courier New', monospace; background-color: #0a0a0a; color: #e0e0e0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 30px;">
                <h2 style="color: #b7410e; text-align: center; letter-spacing: 2px;">
                    🔐 FORENSIC PORTAL
                </h2>
                
                <p style="font-size: 14px; line-height: 1.6;">
                    {greeting}
                </p>
                
                <p style="font-size: 14px; line-height: 1.6;">
                    Your account has been successfully created! Here are your login credentials:
                </p>
                
                <div style="background-color: #0f0f0f; border: 1px solid #b7410e; border-radius: 4px; padding: 20px; margin: 20px 0;">
                    <p style="margin: 10px 0;">
                        <strong style="color: #fbbf24;">UID:</strong> 
                        <code style="background-color: #000; padding: 5px 10px; border-radius: 3px; font-size: 16px; color: #22c55e;">
                            {uid}
                        </code>
                    </p>
                    
                    <p style="margin: 10px 0;">
                        <strong style="color: #fbbf24;">Email:</strong> 
                        <span style="color: #60a5fa;">{to_email}</span>
                    </p>
                    
                    <p style="margin: 10px 0;">
                        <strong style="color: #fbbf24;">Today's Password:</strong> 
                        <code style="background-color: #000; padding: 5px 10px; border-radius: 3px; font-size: 16px; color: #22c55e;">
                            {password}
                        </code>
                    </p>
                </div>
                
                <div style="background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0;">
                    <p style="font-size: 12px; margin: 5px 0;">
                        ⚠️ <strong>IMPORTANT:</strong> Your password changes daily for security.
                    </p>
                    <p style="font-size: 12px; margin: 5px 0;">
                        💡 Use your UID to login and retrieve new passwords each day.
                    </p>
                    <p style="font-size: 12px; margin: 5px 0;">
                        🔒 Never share your UID with anyone.
                    </p>
                </div>
                
                <p style="font-size: 14px; line-height: 1.6; text-align: center; margin-top: 30px;">
                    <a href="http://localhost:5173/login" 
                       style="background-color: #b7410e; color: #fff; padding: 12px 30px; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: bold; letter-spacing: 1px;">
                        LOGIN NOW →
                    </a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #333; margin: 30px 0;">
                
                <p style="font-size: 11px; color: #666; text-align: center;">
                    Forensic Analysis Portal v2.1<br>
                    This is an automated message. Do not reply to this email.
                </p>
            </div>
        </body>
    </html>
    """
    
    text_content = f"""
    FORENSIC PORTAL - Your Account Credentials
    ================================================
    
    {greeting}
    
    Your account has been successfully created!
    
    LOGIN CREDENTIALS:
    ------------------
    UID: {uid}
    Email: {to_email}
    Today's Password: {password}
    
    IMPORTANT NOTES:
    ----------------
    ⚠️ Your password changes daily for security.
    💡 Use your UID to login and retrieve new passwords each day.
    🔒 Never share your UID with anyone.
    
    Login at: http://localhost:5173/login
    
    ---
    Forensic Analysis Portal v2.1
    This is an automated message. Do not reply.
    """
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"Forensic Portal <{SENDER_EMAIL}>"
        message["To"] = to_email
        
        # Attach both text and HTML versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email via SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        return {
            "success": True,
            "message": f"Credentials sent to {to_email}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}"
        }


# Test function (for development only)
if __name__ == "__main__":
    result = send_credentials_email(
        to_email="test@kmit.edu.in",
        uid="KMIT123456",
        password="AB12cd34@",
        full_name="Test User"
    )
    print(result)
