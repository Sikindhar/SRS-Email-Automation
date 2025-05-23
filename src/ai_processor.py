import cohere
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class AIProcessor:
    def __init__(self):
        self.co = cohere.Client(os.getenv('COHERE_API_KEY'))
        
    def generate_requirements(self, email_data):
        """Generate SRS from email content"""
        prompt = self._create_prompt(email_data)
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            return self._parse_ai_response(response.generations[0].text)
            
        except Exception as e:
            print(f"Error generating requirements: {str(e)}")
            return None
    
    def _create_prompt(self, email_data):
        return f"""
        Generate a detailed software requirements specification document for the following request.
        Format your response with these exact section headers:

        Project Overview:
        [Write a brief overview of the project]

        Functional Requirements:
        [List all functional requirements]

        Technical Specifications:
        [List all technical specifications]

        Test Cases:
        [List key test scenarios]

        Timeline:
        [Provide project timeline]

        Cost Estimation:
        [Provide cost breakdown]

        Resource Requirements:
        [List required resources]

        Original Request:
        {email_data['body']}
        """

    def _parse_ai_response(self, response):
        """Parse AI response into sections"""
        text = response
        sections = {}
        current_section = None
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            if line.strip().endswith(':'):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.strip()[:-1].lower().replace(' ', '_')
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return {
            'raw_response': response,
            'timestamp': datetime.now().isoformat(),
            'sections': {
                'project_overview': sections.get('project_overview', ''),
                'functional_requirements': sections.get('functional_requirements', ''),
                'technical_specs': sections.get('technical_specifications', ''),
                'test_cases': sections.get('test_cases', ''),
                'timeline': sections.get('timeline', ''),
                'cost_estimation': sections.get('cost_estimation', ''),
                'resources': sections.get('resource_requirements', '')
            }
        }