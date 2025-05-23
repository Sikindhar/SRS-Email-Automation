from email_handler import EmailHandler
import os

def test_authentication():
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for credentials.json in: {os.path.abspath('credentials.json')}")
    
    try:
        handler = EmailHandler()
        print("Email handler initialized successfully")
        return True
    except Exception as e:
        print(f"Authentication test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_authentication()