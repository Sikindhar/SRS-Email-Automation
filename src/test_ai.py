from ai_processor import AIProcessor

def test_ai_processing():
    print("Testing AI Processor...")
    processor = AIProcessor()
    
    test_email = {
        'sender': 'test_exaample@gmail.com',  
        'subject': 'Resume Form Requirements',
        'body': '''Please create a resume form with:
        1. User information fields
        2. File upload capability
        3. Email notification system
        5. CAPTCHA integration
        
        Additional requirements:
        - Must be mobile responsive 
        - Should integrate with existing CRM
        - We must finish the project in 3 working days
        - Need automated email confirmations''',
        'date': '2025-05-20'
    }
    
    result = processor.generate_requirements(test_email)
    if result:
        print("\nGenerated Requirements:")
        print(result['raw_response'])
    else:
        print("Failed to generate requirements")

if __name__ == "__main__":
    test_ai_processing()