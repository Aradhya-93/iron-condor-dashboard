from kiteconnect import KiteConnect
import os


# 🔐 Your Zerodha API credentials
API_KEY = os.environ["Z_API_KEY"]
API_SECRET = os.environ["Z_API_SECRET"]
REQUEST_TOKEN = os.environ.get("Z_REQUEST_TOKEN")

def generate_access_token(request_token):
    kite = KiteConnect(api_key=API_KEY)
    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]
        print("\n✅ Your access token (valid for today only):\n")
        print(access_token)
        return access_token
    except Exception as e:
        print("\n❌ Error generating access token:", e)

if __name__ == "__main__":
    # STEP 1: Print login URL
    #login_url = f"https://kite.zerodha.com/connect/login?v=3&api_key={API_KEY}"
    #print("\n🔗 Open this URL in your browser and login to get the request token:")
   # print(login_url)

    # STEP 2: Prompt for request token
   # request_token = input("\n✏️ Paste the 'request_token' from the redirected URL: ").strip()

    # STEP 3: Get access token
    generate_access_token(request_token=REQUEST_TOKEN)
