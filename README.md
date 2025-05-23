# SRS-Email-Automation

## Overview

**SRS-Email-Automation** is an automated tool designed to monitor email inboxes, extract relevant information, and generate Software Requirement Specifications (SRS) using AI. This project streamlines the process of gathering requirements from client emails and converting them into structured SRS documents.

## Features

- Monitors specified email accounts for new messages
- Extracts and summarizes requirements from emails using AI
- Generates SRS documents in markdown or PDF format
- Configurable email filters and triggers
- Logs activity and errors for auditing

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Sikindhar/SRS-Email-Automation.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Configure your email and other settings in `config.yaml`.

## Usage

Run the main script:
```bash
python main.py
```
The application will start monitoring the configured email inbox and generate SRS documents as new requirements arrive.

## Configuration

Edit the `config.yaml` file to set:
- Email server settings
- Output directory for SRS files
- Add your templates:
  requirements: "templates/requirement_template.md"
- create a .env file to add your cohere API key

## Example

Sample workflow:
1. Client sends an email with project requirements.
2. The tool detects the new email, extracts the content, and summarizes requirements.
3. An SRS document is generated and saved to the output directory.

## Contributing

Contributions are welcome! Please open issues for improvements.




