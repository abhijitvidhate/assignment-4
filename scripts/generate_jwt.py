import jwt
import datetime
import sys

def generate_jwt(key, secret):
    payload = {
        "iss": key,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generate_jwt.py <key> <secret>")
        sys.exit(1)
    key = sys.argv[1]
    secret = sys.argv[2]
    print(generate_jwt(key, secret))
