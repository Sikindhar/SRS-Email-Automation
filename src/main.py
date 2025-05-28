import os
import logging
from dotenv import load_dotenv
from email_handler import EmailHandler
from ai_processor import AIProcessor
from db_utils import MongoDB
import asyncio


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


load_dotenv()

class EmailMonitor:
    def __init__(self):
        self.email_handler = EmailHandler()
        self.ai_processor = AIProcessor()
        self.db = MongoDB()
        logger.info("Email Monitor initialized successfully")

    async def process_request(self, email_content):
        """Process incoming email request"""
        try:
            logger.info(f"Processing request from: {email_content['sender']}")
            
            sender_email = email_content['sender'].split('<')[-1].replace('>', '')
            if not self.db.is_email_approved(sender_email):
                logger.warning(f"Rejected unauthorized sender: {sender_email}")
                return False
            
            result = self.ai_processor.generate_requirements(email_content)
            
            if result:
                self.email_handler.send_response(result, email_content['sender'])
                logger.info(f"Processed request from {email_content['sender']}")
                logger.info(f"Document sent: {result['filename']}")
                return True
            else:
                logger.error("Failed to generate requirements")
                return False
                
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return False

    async def start_monitoring(self):
        """Start monitoring emails"""
        logger.info("Starting email monitoring...")
        while True:
            try:
                await self.email_handler.start_monitoring(self.process_request)
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying

def main():
    try:
        logger.info("Starting Email Automation System")
        monitor = EmailMonitor()
        
        asyncio.run(monitor.start_monitoring())
        
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()