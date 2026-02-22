"""Test passlib hash identification"""
from passlib.context import CryptContext

# Same config as auth.py
ctx = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')

# Hash from database
h = '$pbkdf2-sha256$29000$NaY0JoSwdu5dS2kNAaAUQg$sSTvW5edbGX7nlpwkms4Rki52OkhIAGqOubPOybV1G0'

print("Hash:", h[:50] + "...")
print("Len:", len(h))

# Test identification
try:
    identified = ctx.identify(h)
    print("Identify result:", identified)
except Exception as e:
    print("Identify FAILED:", e)

# Try verification
try:
    result = ctx.verify("admin123", h)
    print("Verify result:", result)
except Exception as e:
    print("Verify FAILED:", e)

# Generate a new hash and compare format
new_hash = ctx.hash("admin123")
print("\nNew hash format:", new_hash[:50] + "...")
print("New hash len:", len(new_hash))

# Compare prefixes
print("\nDB hash prefix:", h[:20])
print("New hash prefix:", new_hash[:20])
