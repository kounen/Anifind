# Import secrets module (Generate secure random numbers for managing secrets)
import secrets

def generate_code_challenge_verifier() -> str:
    # Return a random URL-safe text string, containing 128 random bytes (maximum length handled by MAL's API)
    return secrets.token_urlsafe(96)

# Code challenge is the same as the code verifier with the "plain" method
code_challenge = code_verifier = generate_code_challenge_verifier()

print(len(code_challenge))
print(code_challenge)
