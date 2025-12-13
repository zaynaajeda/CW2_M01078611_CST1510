# Author

- Student Name: AJEDA Bibi Zayna
- Student ID: M01078611
- Course: CST1510 - CW2  

# Multi-Domain Intelligence Platform
This repository contains the source code, all attached and necessary files, video demonstration and documentation for the intelligence platform.

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