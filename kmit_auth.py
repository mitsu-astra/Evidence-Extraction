"""
KMIT CUSTOM AUTHENTICATION
Handles KMIT-specific auth: email verification, UID generation, daily passwords
"""

from supabase import create_client, Client
import os
import hashlib
from datetime import datetime, date
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Import email service
try:
    from email_service import send_credentials_email
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False
    # Stub function when email service not available
    def send_credentials_email(to_email: str, uid: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        return {"success": False, "message": "Email service not configured"}

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)  # type: ignore
    return _supabase_client


# ═══════════════════════════════════════════════════════════════════════════
#  PASSWORD GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def generate_daily_password(uid: str, target_date: Optional[date] = None) -> str:
    """
    Generate a deterministic password that changes daily.
    
    Algorithm:
    - Combine UID + date + secret salt
    - Hash with SHA256
    - Take first 8 characters + add special char
    - Result: ABC12de@
    
    Args:
        uid: User's unique ID
        target_date: Date for password (defaults to today)
    
    Returns:
        8-character password
    """
    if target_date is None:
        target_date = date.today()
    
    # Secret salt (should be in environment variable)
    SECRET_SALT = os.getenv("KMIT_PASSWORD_SALT", "KMIT_FORENSIC_2026_SECRET")
    
    # Combine UID + date + salt
    date_str = target_date.strftime("%Y%m%d")
    raw_string = f"{uid}{date_str}{SECRET_SALT}"
    
    # Generate hash
    hash_object = hashlib.sha256(raw_string.encode())
    hash_hex = hash_object.hexdigest()
    
    # Take first 8 chars and format
    # Mix uppercase, lowercase, numbers
    password = (
        hash_hex[0:2].upper() +    # 2 uppercase letters
        hash_hex[2:4] +              # 2 digits/letters
        hash_hex[4:6].lower() +      # 2 lowercase letters
        hash_hex[6:8] +              # 2 more chars
        "@"                          # Special character
    )
    
    return password[:8] + "@"


# ═══════════════════════════════════════════════════════════════════════════
#  NEW USER SIGNUP
# ═══════════════════════════════════════════════════════════════════════════

def signup_new_user(email: str, full_name: Optional[str] = None, department: Optional[str] = None) -> Dict[str, Any]:
    """
    Register a new KMIT user.
    
    Flow:
    1. Validate email ends with @kmit.edu.in
    2. Generate unique UID (KMIT + 6 digits)
    3. Create user record
    4. Generate today's password
    5. Return credentials
    
    Args:
        email: User's KMIT email address
        full_name: User's full name (optional)
        department: Department code (optional)
    
    Returns:
        {
            "success": True/False,
            "uid": "KMIT123456",
            "email": "user@kmit.edu.in",
            "password": "ABC12de@",
            "message": "Account created successfully",
            "error": None or error message
        }
    """
    # Validate email domain
    if not email.lower().endswith('@kmit.edu.in'):
        return {
            "success": False,
            "error": "Only @kmit.edu.in email addresses are allowed",
            "uid": None,
            "email": email,
            "password": None,
        }
    
    supabase = get_supabase_client()
    
    try:
        # Check if email already exists
        existing = supabase.table("kmit_users").select("uid").eq("email", email).execute()
        if existing.data:  # type: ignore
            return {
                "success": False,
                "error": "Email already registered. Please login with your UID.",
                "uid": existing.data[0].get("uid"),  # type: ignore
                "email": email,
                "password": None,
            }
        
        # Generate unique UID by calling database function
        uid_result = supabase.rpc("generate_uid").execute()
        new_uid = uid_result.data  # type: ignore
        
        # Create user record
        user_data = {
            "uid": new_uid,
            "email": email.lower(),
            "full_name": full_name,
            "department": department,
            "is_active": True,
        }
        
        result = supabase.table("kmit_users").insert(user_data).execute()
        
        # Generate today's password
        password = generate_daily_password(new_uid)  # type: ignore
        
        # Log password generation (optional)
        supabase.table("kmit_password_logs").insert({
            "uid": new_uid,
            "used": False
        }).execute()
        
        # Send credentials via email (if configured)
        email_sent = False
        email_message = ""
        if EMAIL_ENABLED:
            email_result = send_credentials_email(
                to_email=email,
                uid=new_uid,  # type: ignore
                password=password,
                full_name=full_name
            )
            email_sent = email_result.get("success", False)
            email_message = email_result.get("message", "")
        
        success_msg = f"Account created! Your UID is {new_uid}."
        if email_sent:
            success_msg += f" Credentials sent to {email}."
        else:
            success_msg += " Save your credentials - they are shown below."
        
        return {
            "success": True,
            "uid": new_uid,
            "email": email,
            "password": password,
            "message": success_msg,
            "email_sent": email_sent,
            "email_message": email_message,
            "error": None,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Signup failed: {str(e)}",
            "uid": None,
            "email": email,
            "password": None,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  EXISTING USER LOGIN
# ═══════════════════════════════════════════════════════════════════════════

def login_existing_user(uid: str) -> Dict[str, Any]:
    """
    Login for existing KMIT users using UID.
    
    Flow:
    1. Validate UID exists
    2. Generate today's password
    3. Return credentials
    
    Args:
        uid: User's unique ID (e.g., "KMIT123456")
    
    Returns:
        {
            "success": True/False,
            "uid": "KMIT123456",
            "email": "user@kmit.edu.in",
            "password": "ABC12de@",
            "full_name": "John Doe",
            "message": "Login successful",
            "error": None or error message
        }
    """
    supabase = get_supabase_client()
    
    try:
        # Fetch user by UID
        result = supabase.table("kmit_users").select("*").eq("uid", uid.upper()).execute()
        
        if not result.data:  # type: ignore
            return {
                "success": False,
                "error": "UID not found. Please signup first.",
                "uid": uid,
                "email": None,
                "password": None,
                "full_name": None,
            }
        
        user = result.data[0]  # type: ignore
        
        # Check if user is active
        if not user.get("is_active"):  # type: ignore
            return {
                "success": False,
                "error": "Account is disabled. Contact administrator.",
                "uid": uid,
                "email": user.get("email"),  # type: ignore
                "password": None,
                "full_name": user.get("full_name"),  # type: ignore
            }
        
        # Generate today's password
        password = generate_daily_password(uid.upper())
        
        # Update last login time
        supabase.table("kmit_users").update({
            "last_login": datetime.utcnow().isoformat()
        }).eq("uid", uid.upper()).execute()
        
        # Log password generation
        supabase.table("kmit_password_logs").insert({
            "uid": uid.upper(),
            "used": True
        }).execute()
        
        return {
            "success": True,
            "uid": user.get("uid"),  # type: ignore
            "email": user.get("email"),  # type: ignore
            "password": password,
            "full_name": user.get("full_name"),  # type: ignore
            "department": user.get("department"),  # type: ignore
            "message": f"Login successful! Today's password: {password}",
            "error": None,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Login failed: {str(e)}",
            "uid": uid,
            "email": None,
            "password": None,
            "full_name": None,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  VERIFY PASSWORD
# ═══════════════════════════════════════════════════════════════════════════

def verify_password(uid: str, password: str) -> bool:
    """
    Verify if provided password matches today's generated password.
    
    Args:
        uid: User's unique ID
        password: Password to verify
    
    Returns:
        True if password is correct, False otherwise
    """
    expected_password = generate_daily_password(uid.upper())
    return password == expected_password


# ═══════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_user_by_uid(uid: str) -> Optional[Dict[str, Any]]:
    """Fetch user details by UID."""
    supabase = get_supabase_client()
    try:
        result = supabase.table("kmit_users").select("*").eq("uid", uid.upper()).execute()
        return result.data[0] if result.data else None  # type: ignore
    except Exception:
        return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetch user details by email."""
    supabase = get_supabase_client()
    try:
        result = supabase.table("kmit_users").select("*").eq("email", email.lower()).execute()
        return result.data[0] if result.data else None  # type: ignore
    except Exception:
        return None


def deactivate_user(uid: str) -> bool:
    """Deactivate a user account."""
    supabase = get_supabase_client()
    try:
        supabase.table("kmit_users").update({"is_active": False}).eq("uid", uid.upper()).execute()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    print("═" * 80)
    print(" KMIT AUTHENTICATION SYSTEM - TEST")
    print("═" * 80)
    
    # Test signup
    print("\n1. Testing Signup...")
    result = signup_new_user("test.student@kmit.edu.in", "Test Student", "CSE")
    print(f"   Result: {result}")
    
    if result["success"]:
        uid = result["uid"]
        
        # Test login
        print(f"\n2. Testing Login with UID: {uid}")
        login_result = login_existing_user(uid)
        print(f"   Result: {login_result}")
        
        # Test password verification
        print(f"\n3. Testing Password Verification...")
        is_valid = verify_password(uid, login_result["password"])
        print(f"   Password valid: {is_valid}")
    
    print("\n" + "═" * 80)
