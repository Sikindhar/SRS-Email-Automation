import cohere
import os
from dotenv import load_dotenv
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from io import BytesIO

load_dotenv()

class AIProcessor:
    def __init__(self):
        self.co = cohere.Client(os.getenv('COHERE_API_KEY'))
        self.styles = getSampleStyleSheet()
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['Normal'],
            leftIndent=20,
            firstLineIndent=-10,
            spaceBefore=6,
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2E4053')
        ))

    def extract_core_message(self, email_body):
        """Extract the core message and requirements from email content"""
        try:
            prompt = f"""
            As an expert requirements analyst, analyze this email and extract the core message and key requirements.
            Focus on identifying:
            1. Main project objectives
            2. Key features requested
            3. Technical requirements
            4. Business constraints
            5. Timeline expectations
            6. Budget considerations

            EMAIL CONTENT:
            {email_body}

            Provide a concise summary in the following format:
            CORE OBJECTIVE: [Main goal of the project]
            KEY FEATURES: [List of main features]
            TECHNICAL NEEDS: [Technical requirements]
            CONSTRAINTS: [Business/technical constraints]
            TIMELINE: [Time expectations]
            BUDGET: [Budget considerations]

            If any section is not mentioned in the email, indicate 'Not specified'.""".strip()

            response = self.co.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more focused extraction
                k=0,
                p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                stop_sequences=[],
                return_likelihoods='NONE'
            )

            return response.generations[0].text.strip()

        except Exception as e:
            print(f"Error extracting core message: {str(e)}")
            return None

    def generate_requirements(self, email_data):
        """Generate SRS from email content"""
        try:
            email_body = email_data if isinstance(email_data, str) else email_data.get('body', '')
            
            core_message = self.extract_core_message(email_body)
            if not core_message:
                print("Warning: Could not extract core message, proceeding with full email content")
                core_message = "No core message extracted"
            
            prompt = f"""
            As an expert software requirements analyst, generate a comprehensive Software Requirements Specification (SRS) document.
            Use the extracted core message and full email content to create detailed requirements.
            For any missing information, provide industry-standard recommendations.

            EXTRACTED CORE MESSAGE:
            {core_message}

            FULL EMAIL CONTENT:
            {email_body}

            INSTRUCTIONS:
            Generate a detailed SRS document with the following sections. Use bullet points for all items and ensure each point is a complete sentence.

            1. Project Overview
            • Provide project background
            • State clear objectives
            • Define project scope

            2. Functional Requirements
            • List all core features
            • Define user roles and permissions
            • Describe main workflows

            3. Technical Specifications
            • Detail system architecture
            • List technology requirements
            • Specify security considerations

            4. Test Cases
            • Define key test scenarios
            • Outline testing approach
            • List acceptance criteria

            5. Implementation Details
            • Describe development approach
            • Outline deployment strategy
            • List integration requirements

            6. Timeline
            • Break down project phases
            • List key milestones
            • Define delivery dates

            7. Cost Estimation
            • Break down development costs
            • List infrastructure costs
            • Include maintenance estimates

            8. Resources
            • Define team structure
            • List required skills
            • Specify tools and resources

            Format each section with clear bullet points and complete sentences.
            Make the content practical and actionable.
            Include industry standards for any missing information.
            Ensure all requirements align with the core message and business objectives.""".strip()
            
            response = self.co.generate(
                prompt=prompt,
                max_tokens=4000,
                temperature=0.7,
                k=0,
                p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            generated_text = response.generations[0].text.strip()
            
            pdf_bytes = self._generate_pdf(generated_text)
            
            return {
                'text': generated_text,
                'pdf_bytes': pdf_bytes,
                'filename': f"srs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                'core_message': core_message  
            }
                
        except Exception as e:
            print(f"Error generating requirements: {str(e)}")
            return None

    def _generate_pdf(self, content):
        """Generate PDF in memory"""
        try:
            buffer = BytesIO()
            
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            MyText = []
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Title'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#1A5276')
            )
            MyText.append(Paragraph("Software Requirements Specification", title_style))
            MyText.append(Spacer(1, 12))
            
            date_style = ParagraphStyle(
                'CustomDate',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.gray
            )
            MyText.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
            MyText.append(Spacer(1, 24))
            
            current_section = None
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    

                if line[0].isdigit() and '. ' in line[:3]:
                    if current_section:
                        MyText.append(Spacer(1, 12))
                    current_section = line
                    MyText.append(Paragraph(current_section, self.styles['SectionHeader']))
                elif line.startswith('•'):
                    MyText.append(Paragraph(line, self.styles['CustomBullet']))
                else:
                    MyText.append(Paragraph(line, self.styles['Normal']))
            
            doc.build(MyText)
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
                
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return None