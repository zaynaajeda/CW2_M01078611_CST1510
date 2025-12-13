# Author

- Student Name: AJEDA Bibi Zayna
- Student ID: M01078611
- Course: Computer Science (Year 1)
- Module: CST1510 - Coursework 2 - Programming for Data Communication and Networks  

# Multi-Domain Intelligence Platform
This repository contains the source code, all attached and necessary files and documentation for the intelligence platform. Video demonstration is available in 'vid_demo' folder.

## Overview and Project Description
The project offers a user-friendly website where user can create account, login and view records for 3 domains (Cybersecurity, Data Science and IT Operations). The web platform uses role-based access control where account is registered as user, admin or analyst for a domain. It exposes CRUD operations for each domain only for admins and domain-specialised analysts. Users can view table, charts and graph for each domain. There is also AI features which help in generating overall AI insights about each domain and for each record in domain as well. There is a chatbox where user can interact with OpenAI assistant. There, user can choose what AI Assitant he wants to operate. In Settings, there is the option of changing password. Administrative tools for user management are only available to admins in Settings.

## Features
### User Authentication
- Streamlit-based registration/login with bcrypt, hashing, username and password validations
- User registration with duplicate username prevention
- Secure password hashing using bcrypt with automatic salt generation
- User login with password verification
- Input validation for usernames and passwords
- File-based user data persistence

### Role-Based Access Control
- Use of roles (user, admin and analyst) upon registration
- analyst has a domain speciality
- user only view data, cannot access CRUD functions for domain and cannot get AI analysis for a record in domain as well as view user management.
- analyst can only access CRUD and AI record analysis for his domain and cannot access user management
- admin has no restraints and can have access to all features in the web application.

### CRUD Operation
- Ability to add, update and delete record for each domain
- Use of SQLite

### Data Visualisations
- Table for each domain in dashboard
- Summarised metrics shown above table in dasboard
- One time-series graph, bar charts and pie charts for each domain in Analytics

### OpenAI Integration
- OpenAI Assistant that analyse data in dashboard and analytics to give insights
- AI Assistants give insight about selected record in AI-Enhanced Analysis
- Chat with AI Assistant - User can choose speciality of AI

## Technical Implementation
- Hashing Algorithm: bcrypt with automatic salting
- Data Storage: Plain text file ('users.txt') with comma-separated values
- Password Security: One-way hashing, no plaintext storage
- Validation: Username (3-20 alphanumeric characters), Password (6-50 characters)
- CRUD Operations: SQLite functions in schema and in each domain
- Open AI: AI modules
- UI: Streamlit multiple pages with GUI
- Synchronisation: Flat-file storage and SQLite Database are up to date

## Technologies Used
- Programming language: Python
- Framework: Streamlit
- Database: SQLite
- Libraries mentionend in requirements.txt

## System Architecture
- Presentation layer: Streamlit UI
- Application layer: Coding parts
- Data layer: SQLite Database, csv, txt files

## Project Structure
.
├── DATA
│   ├── cyber_incidents.csv
│   ├── datasets_metadata.csv
│   ├── intelligence_platform.db
│   ├── it_tickets.csv
│   ├── lockouts.txt
│   └── users.txt
├── app
│   ├── data
│   │   ├── datasets.py
│   │   ├── db.py
│   │   ├── incidents.py
│   │   ├── schema.py
│   │   ├── tickets.py
│   │   └── users.py
│   └── services
│       ├── auth.py
│       └── user_service.py
├── docs
│   └── README.md
├── models
│   ├── auth.py
│   ├── datasets.py
│   ├── incidents.py
│   └── tickets.py
├── my_app
│   ├── Home.py
│   ├── components
│   │   ├── ai_functions.py
│   │   └── sidebar.py
│   └── pages
│       ├── 1_Dashboard.py
│       ├── 2_Analytics.py
│       ├── 3_AI_Enhanced_Analysis.py
│       ├── 4_AI_Assistant.py
│       └── 5_Settings.py
├── vid_demo
│   └── CST1510Vid_Demo.mp4
├── main.py
├── requirements.txt
└── venv
    ├── bin/…
    ├── lib/python3.13/site-packages/…
    └── (standard virtual env folders)

## Streamlit Platform
Key pages:
- **Home:** Login/Register tabs
- **Dashboard:** Domain choice, metrics, table and forms for CRUD functions
- **Analytics:** Time-series graph, bar charts and pie charts for domain
- **AI Enhanced Analysis:** OpenAI summaries of charts and table
- **AI Assistant:** Chat with AI assistant tailored with domains or general AI
- **Settings:** Profile overview and form to change password, admin utilities for user management

## Installations
(In Terminal of VS code)
- Install all required libraries:
```bash
pip install -r requirements.txt
```
- Prepare Streamlit secrets for OpenAI, Create a file secrets.toml inside a folder .streamlit:
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY="sk-replace-with-your-own-key"
```

## Running the Application
- Open terminal
- Ensure it is in root directory that is CW2_M01078611_CST1510
- Run the command:
```bash
streamlit run my_app/Home.py
```

## Accounts on Application
### Admin
- **Username:** Zayna
- **Password:** StrongPassword1!

### Analyst for Cybersecurity
- **Username:** alice
- **Password:** SecurePass123

### User
- **Username:** ana
- **Password:** SecurePass123

## Troubleshooting
- **`OPENAI_API_KEY` Key Error:** Ensure `.streamlit/secrets.toml` exists with `OPENAI_API_KEY`
- **MISSING DATA FILES:** Run `main.py` in database to recreate database