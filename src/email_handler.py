import os
import base64
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify'  ]

class EmailHandler:
    def __init__(self):
        self.creds = None
        self.service = None
        self._load_config()
        self._authenticate()

    def _load_config(self):
        try:
            with open('config/config.yaml', 'r') as file:
                self.config = yaml.safe_load(file)['email']
        except FileNotFoundError:
            raise Exception("config.yaml not found in config directory")
        except KeyError:
            raise Exception("'email' configuration missing in config.yaml")
    
    def _authenticate(self):
        """Handle Gmail API authentication using existing token or new OAuth flow"""
        try:
            print("Starting authentication process...")
            
            if os.path.exists('token.json'):
                print("Found existing token.json, attempting to use it...")
                self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
                
                # Only refresh if token is expired
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    print("Token expired, refreshing...")
                    self.creds.refresh(Request())
                    # Save refreshed token
                    with open('token.json', 'w') as token:
                        token.write(self.creds.to_json())
            else:
                print("No token.json found, starting new authentication flow...")
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError("credentials.json not found")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', 
                    SCOPES
                )
                self.creds = flow.run_local_server(
                    port=8080,
                    success_message='Authentication successful! You can close this window.'
                )
                
                print("Saving new token.json")
                with open('token.json', 'w') as token:
                    token.write(self.creds.to_json())

            self.service = build('gmail', 'v1', credentials=self.creds)
            print("Authentication successful!")
                
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
        

    def _validate_email(self, email_content):
        """Validate incoming email requests"""
        try:
            approved_emails = [
                'spatibandla10@gmail.com',
                '',#wecan add others or add domain restrictions
                'sikindharjaladi@gmail.com'
            ]

            sender_email = email_content['sender'].split('<')[-1].replace('>', '')
            
            validations = {
                'approved_sender': sender_email in approved_emails,
                'has_subject': len(email_content['subject'].strip()) > 0,
                'has_body': len(email_content['body'].strip()) > 0,
            }
            
            if not validations['approved_sender']:
                print(f"Rejected unauthorized sender: {sender_email}")
            
            return all(validations.values()), validations
                
        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False, {}


    def parse_email(self, email_content):
        """Parse email content to extract relevant information"""
        return {
            'subject': email_content.get('subject', ''),
            'body': email_content.get('body', ''),
            'sender': email_content.get('sender', ''),
            'received_date': email_content.get('date', '')
        }

    def send_response(self, docs, recipient):
        """Send generated PDF document back to the sender"""
        try:
            message = MIMEMultipart()
            message['to'] = recipient
            message['from'] = self.config['sender_email']
            message['subject'] = 'Your Requirements Specification Document'
            
            body = """
            Hello,
            
            Thank you for your request. Please find attached the generated requirements specification document.
            
            Best regards,
            AI Requirements Generator
            """
            message.attach(MIMEText(body, 'plain'))

            with open(docs['file_path'], 'rb') as f:
                pdf = MIMEBase('application', 'octet-stream')
                pdf.set_payload(f.read())
                encoders.encode_base64(pdf)
            
            filename = os.path.basename(docs['file_path'])
            pdf.add_header(
                'Content-Disposition',
                f'attachment; filename="{filename}"'
            )
            pdf.add_header('Content-Type', 'application/pdf')
            message.attach(pdf)

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            print(f"Successfully sent document: {filename}")
            return True

        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
        

    def _send_rejection(self, email_content, validations):
        """Send rejection email with explanation"""
        try:
            message = MIMEMultipart()
            message['to'] = email_content['sender']
            message['subject'] = 'Requirements Request - Validation Failed'
            
            rejection_reasons = []
            if not validations.get('approved_sender'):
                rejection_reasons.append("- Email address not in approved list")
            if not validations.get('has_subject'):
                rejection_reasons.append("- Missing subject")
            if not validations.get('has_body'):
                rejection_reasons.append("- Missing body content")
            if not validations.get('valid_request'):
                rejection_reasons.append("- Subject must contain one of: 'requirements', 'specification', 'project', 'document'")
            
            body = f"""
            Dear Sender,
            
            Your requirements request could not be processed for the following reasons:
            {chr(10).join(rejection_reasons)}
            
            Please ensure your email meets all requirements and try again.
            
            Best regards,
            AI Requirements Generator
            """
            
            message.attach(MIMEText(body, 'plain'))
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            print(f"Sent rejection email to: {email_content['sender']}")
            return True
            
        except Exception as e:
            print(f"Error sending rejection email: {str(e)}")
            return False    

    def start_monitoring(self, callback):
        """Monitor inbox for new incoming emails only"""
        print("Starting real-time email monitoring for new messages...")
        
        start_time = int(time.time() * 1000)  
        
        try:
            while True:
                query = f'is:unread after:{int(start_time/1000)}'
                results = self.service.users().messages().list(
                    userId='me',
                    q=query
                ).execute()
                
                messages = results.get('messages', [])
                if messages:
                    print(f"Found {len(messages)} new unread messages")
                    
                for message in messages:
                    try:
                        msg = self.service.users().messages().get(
                            userId='me',
                            id=message['id']
                        ).execute()
                        
                        message_time = int(msg['internalDate'])
                        if message_time > start_time:
                            start_time = message_time
                        
                        email_content = self._extract_email_content(msg)
                        is_valid, validations = self._validate_email(email_content)
                        
                        if is_valid:
                            print(f"Processing new request from: {email_content['sender']}")
                            callback(email_content)
                        else:
                            print(f"Invalid request from: {email_content['sender']}")
                            self._send_rejection(email_content, validations)
                        
                        self.service.users().messages().modify(
                            userId='me',
                            id=message['id'],
                            body={'removeLabelIds': ['UNREAD']}
                        ).execute()
                        
                    except Exception as e:
                        print(f"Error processing message: {str(e)}")
                        continue
                
                sleep_time = self.config.get('monitoring_interval', 60)
                print(f"Waiting {sleep_time} seconds for new emails...")
                time.sleep(sleep_time)
                    
        except Exception as e:
            print(f"Monitoring error: {str(e)}")
            time.sleep(self.config.get('retry_interval', 60))

    def _extract_email_content(self, message):
        """Extract content from Gmail message object"""
        try:
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            
            parts = message['payload'].get('parts', [])
            body = ''
            
            if not parts:  
                if 'data' in message['payload'].get('body', {}):
                    body = base64.urlsafe_b64decode(
                        message['payload']['body']['data']
                    ).decode()
            else:
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body = base64.urlsafe_b64decode(
                                part['body']['data']
                            ).decode()
                            break
            
            return {
                'subject': subject,
                'body': body,
                'sender': sender,
                'date': message['internalDate']
            }
            
        except Exception as e:
            print(f"Error extracting email content: {str(e)}")
            return {
                'subject': 'Error',
                'body': 'Could not extract email content',
                'sender': 'Unknown',
                'date': None
            }