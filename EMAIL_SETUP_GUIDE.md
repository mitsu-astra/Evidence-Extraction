# EMAIL CONFIGURATION GUIDE

## Quick Setup: Gmail (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow steps to enable 2FA

### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "App": Mail
3. Select "Device": Other (Custom name) → "Forensic Portal"
4. Click "Generate"
5. Copy the 16-character password (no spaces)

### Step 3: Update .env File
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=youremail@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop  # Paste the 16-char app password (remove spaces)
```

### Step 4: Restart Backend
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
.venv\Scripts\Activate.ps1
python forensic_web_app.py
```

## Features

✅ **Automatic Email Delivery**
- Users receive UID + password immediately after signup
- Beautifully formatted HTML email
- Daily password reminder included

✅ **Professional Email Template**
- KMIT branding with dark theme
- Clear credential display
- Security reminders
- Direct login link

✅ **Fallback Behavior**
- If email not configured: Credentials shown on screen only
- If email fails: Credentials still shown on screen
- No impact on signup process

## Alternative: Other Email Providers

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=youremail@outlook.com
SENDER_PASSWORD=your-password
```

### Custom SMTP Server
```env
SMTP_SERVER=mail.yourserver.com
SMTP_PORT=587  # or 465 for SSL
SENDER_EMAIL=noreply@yourdomain.com
SENDER_PASSWORD=your-smtp-password
```

## Testing Email

Run this in Python terminal:
```python
from email_service import send_credentials_email

result = send_credentials_email(
    to_email="test@kmit.edu.in",
    uid="KMIT123456",
    password="AB12cd34@",
    full_name="Test User"
)
print(result)
```

## Troubleshooting

**"535 Authentication failed"**
→ Double-check app password (not regular password)

**"Connection refused"**
→ Check firewall/antivirus blocking port 587

**"Email not sending but signup works"**
→ Normal! Email is optional. Check console logs for details.

## Production Recommendations

1. Use dedicated email service (SendGrid, AWS SES, Mailgun)
2. Add email queue for better reliability
3. Implement email verification workflow
4. Add rate limiting to prevent spam

## Disable Email (Optional)

To disable email sending:
- Leave `SENDER_EMAIL` or `SENDER_PASSWORD` blank in .env
- System will work normally, showing credentials on screen only
