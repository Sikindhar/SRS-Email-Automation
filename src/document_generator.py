import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import pdfkit
import markdown

class DocumentGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates'))
        
    def create_documents(self, requirements, email_data):
        """Generate SRS document using template and convert to PDF"""
        try:
            template = self.env.get_template('requirement_template.md')
            markdown_content = template.render(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                requirements=requirements['sections'],
                email=email_data,
                config={'contact_email': 'siki.docs@gmail.com'}
            )
            
            os.makedirs('output', exist_ok=True)
            
            base_filename = f"srs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            md_path = os.path.join('output', f"{base_filename}.md")
            pdf_path = os.path.join('output', f"{base_filename}.pdf")
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            html_content = markdown.markdown(markdown_content)
            html_with_style = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        h1 {{ color: #2c3e50; }}
                        h2 {{ color: #34495e; border-bottom: 1px solid #eee; }}
                        code {{ background-color: #f8f9fa; padding: 2px 4px; }}
                    </style>
                </head>
                <body>{html_content}</body>
            </html>
            """
            
            temp_html = os.path.join('output', f"{base_filename}.html")
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_with_style)
            
            pdfkit.from_file(temp_html, pdf_path)
            
            os.remove(temp_html)
            
            return {
                'file_path': pdf_path,
                'content': markdown_content
            }
            
        except Exception as e:
            print(f"Error generating document: {str(e)}")
            return None