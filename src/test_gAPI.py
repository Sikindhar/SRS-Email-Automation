from ai_processor import AIProcessor

def test_requirements_generation():
    processor = AIProcessor()
    
    test_email = {
        'subject': 'New Contact Form Feature Request',
        'body': 'We need a contact form that collects user information and sends it to our CRM system.'
    }
    
    result = processor.generate_requirements(test_email)
    print(result['raw_response'] if result else "Generation failed")

if __name__ == "__main__":
    test_requirements_generation()