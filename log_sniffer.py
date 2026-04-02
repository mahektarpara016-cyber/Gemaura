import requests

def get_error_log():
    try:
        response = requests.get("http://127.0.0.1:5000/")
        if response.status_code == 500:
            print("=== Homepage 500 Error Body ===")
            # Print first 2000 chars of the error page
            print(response.text[:2000])
        else:
            print(f"Homepage returned status: {response.status_code}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    get_error_log()
