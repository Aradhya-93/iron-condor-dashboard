from kiteconnect import KiteConnect
import json

API_KEY = "your_api_key_here"       # Replace with your API Key
API_SECRET = "your_api_secret_here" # Replace with your API Secret

def save_token(token_data):
    with open("token.json", "w") as f:
        json.dump(token_data, f)
    print("Access token saved to token.json")

def main():
    kite = KiteConnect(api_key=API_KEY)
    print("Login URL:", kite.login_url())

    request_token = input("Enter request_token from login redirect URL: ").strip()
    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        kite.set_access_token(data["access_token"])
        print("Access token:", data["access_token"])

        save_token(data)
    except Exception as e:
        print("Error generating session:", e)

if __name__ == "__main__":
    main()
