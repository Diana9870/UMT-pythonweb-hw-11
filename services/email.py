def send_verification_email(email: str, token: str):
    verify_url = f"http://localhost:8000/api/auth/verify-email?token={token}"
    print(f"Send email to {email}: {verify_url}")