# sghackitrx
Repository for MISS Bot - A tool we developed for SGHackitRx 2024
# Wound Care Management Dashboard
## Overview
This repository contains the code for a Wound Care Management Dashboard built using Streamlit. The dashboard aims to assist healthcare professionals in managing post-operative care for patients by providing recommendations based on wound images and facilitating communication between patients and medical staff.

## Features
* Image Analysis and Recommendations: Provides wound care recommendations based on the analysis of wound images uploaded by the patient.
* Patient Registration: Allows new patients to register and existing patients to update their information.
* Dashboard Visualization: Presents interactive data visualizations to track patient progress and other relevant metrics.
* Database Management: Efficiently handles patient data and wound care history.
* Communication Module: Integrates with Telegram to facilitate real-time communication between patients and healthcare providers.

## File Structure
* app.py: Main entry point for running the Streamlit dashboard.
* dashboard.py: Contains the layout and components for the interactive dashboard.
* database.py: Handles database operations, including patient data and wound history management.
* image.py: Processes and analyzes wound images using image processing and machine learning techniques.
* populate.py: Script for populating the database with initial data.
* registration.py: Manages patient registration and data updating.
* wound_care.py: Contains the logic for wound care recommendations based on image analysis.

## Installation

1. Clone this repository:

* git clone https://github.com/yourusername/wound-care-management.git

2. Navigate to the project directory:
* cd wound-care-management

3. Install the required dependencies:
* pip install -r requirements.txt

4. Usage
To run the dashboard locally, use the following command:
* streamlit run app.py

Open the provided local URL in your browser to interact with the dashboard.
