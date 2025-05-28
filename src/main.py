import os
import logging
from dotenv import load_dotenv
from src.email_handler import EmailHandler
from src.ai_processor import AIProcessor
from src.db_utils import MongoDB
import asyncio
from fastapi import FastAPI
import uvicorn


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


load_dotenv()


app = FastAPI(title="Email SRS Automation")

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
            
            # Check if email is approved
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

monitor = EmailMonitor()

@app.on_event("startup")
async def startup_event():
    """Start email monitoring when the application starts"""
    asyncio.create_task(monitor.start_monitoring())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Email monitoring service is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)