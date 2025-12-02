# Bullying Detection System

A comprehensive system for reporting, validating, and analyzing bullying incidents in schools. This project leverages AI for content analysis and Blockchain for secure, immutable record-keeping.

## Features

- **Role-Based Access Control**:
  - **Reporter (Student)**: Submit reports with description, witness details, and evidence (photo/video).
  - **Admin (School Staff)**: View all reports and manage the system.
  - **Validator (Independent Unit)**: Review escalated reports and validate actions.

- **AI-Powered Analysis**:
  - **Text Analysis**: Detects bullying indicators in report descriptions.
  - **Image Analysis**: Analyzes uploaded evidence for relevant objects/scenes.

- **Blockchain Security**:
  - All actions (Registration, Report Submission, Updates) are recorded on a local blockchain.
  - Ensures data integrity and prevents tampering.

- **Device Binding**:
  - Strict security measure that binds a user's account to the device used during registration.
  - Prevents unauthorized login attempts from other devices.

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python, Flask
- **Data Storage**: JSON-based Blockchain
- **AI Models**: Transformers (Hugging Face)

## Setup Instructions

1.  **Prerequisites**:
    - Python 3.8+
    - pip

2.  **Installation**:
    ```bash
    # Clone the repository (if applicable) or navigate to project folder
    cd /path/to/project

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Running the Application**:
    ```bash
    # Start the backend server
    python3 backend/app.py
    ```
    The server will start at `http://127.0.0.1:5000`.

4.  **Accessing the Frontend**:
    - Open `frontend/index.html` in your browser.
    - Or serve it using a simple HTTP server:
      ```bash
      cd frontend
      python3 -m http.server 8000
      ```
      Then visit `http://localhost:8000`.

## Usage Guide

1.  **Register**: Create an account as a Reporter, Admin, or Validator. **Note**: You must use the same device for login as you did for registration.
2.  **Login**: Access your dashboard.
3.  **Submit Report (Reporter)**: Fill in the details, upload evidence, and submit.
4.  **View Status**: Track the status of your reports.
5.  **Review (Admin/Validator)**: Dashboard to view and act on reports.

## Project Structure

- `backend/`: Flask application and core logic (Blockchain, AI).
- `frontend/`: User interface files.
- `tests/`: Test scripts and verification tools.
