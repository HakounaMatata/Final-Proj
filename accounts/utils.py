from django.core.signing import dumps, loads, BadSignature, SignatureExpired

#For Reset password

SIGN_SALT = "password-reset-magic-link"

def make_reset_token(payload: dict) -> str:
    return dumps(payload, salt=SIGN_SALT)

def read_reset_token(token: str, max_age_seconds: int = 30 * 60) -> dict:
    try:
        return loads(token, salt=SIGN_SALT, max_age=max_age_seconds)
    except SignatureExpired:
        raise ValueError("Reset token expired.")
    except BadSignature:
        raise ValueError("Invalid reset token.")
