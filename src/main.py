import os
from dotenv import load_dotenv
from email_handler import EmailHandler
from ai_processor import AIProcessor
from document_generator import DocumentGenerator
from time import sleep

load_dotenv()

def process_sample_email():
    """Test function to process a sample email"""
    sample_email = {
        'sender': 'spatibandla10@gmail.com',
        'subject': 'New Object in salesforce',
        'body': '''How to create a new object in salesforce and add the validation and phone number fields as per IST format:''',
        'date': '2024-05-20'
    }
    return sample_email

def main(test_mode=True):
    email_handler = EmailHandler()
    ai_processor = AIProcessor()
    doc_generator = DocumentGenerator()
    
    def process_request(email_content):
        try:
            print(f"Processing request from: {email_content['sender']}")
        
            requirements = ai_processor.generate_requirements(email_content)
        
            if requirements:
                docs = doc_generator.create_documents(requirements, email_content)
                
                if docs:
                    email_handler.send_response(docs, email_content['sender'])
                    print(f"Processed request from {email_content['sender']}")
                    print(f"Document saved to: {docs['file_path']}")
                else:
                    print("Failed to generate document")
            else:
                print("Failed to generate requirements")
                
        except Exception as e:
            print(f"Error processing request: {str(e)}")
    
    if test_mode:
        print("Running in test mode...")
        sample_email = process_sample_email()
        process_request(sample_email)
    else:
        print("Starting email monitoring...")
        email_handler.start_monitoring(process_request)

if __name__ == "__main__":
    try:
        print("Starting Email Automation System in Real-time Mode")
        main(test_mode=False)  
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error: {str(e)}")