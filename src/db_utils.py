from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['Email_SRS_Automation']
        self.emails = self.db['approved_emails']

    def add_email(self, email, name=None):
        """Add a new approved email to the database"""
        try:
            if not self.emails.find_one({'email': email}):
                self.emails.insert_one({
                    'email': email,
                    'name': name,
                    'approved': True,
                    'created_at': datetime.now()
                })
                return True
            return False
        except Exception as e:
            print(f"Error adding email: {str(e)}")
            return False

    def is_email_approved(self, email):
        """Check if an email is approved"""
        try:
            return bool(self.emails.find_one({'email': email, 'approved': True}))
        except Exception as e:
            print(f"Error checking email: {str(e)}")
            return False

    def get_all_emails(self):
        """Get all approved emails"""
        try:
            return list(self.emails.find({'approved': True}, {'_id': 0}))
        except Exception as e:
            print(f"Error getting emails: {str(e)}")
            return []

    def remove_email(self, email):
        """Remove an email from approved list"""
        try:
            result = self.emails.delete_one({'email': email})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error removing email: {str(e)}")
            return False 