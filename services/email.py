async def send_verification_email(email: str, token: str):
    print(f"VERIFY: http://localhost:8000/api/auth/verify?token={token}")