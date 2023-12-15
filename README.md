
# Expense Tracker Web App

## Introduction

This is a Flask web application for tracking expenses and managing debts among a group of users. Users can log in, add expenses, view a dashboard summarizing debts, and generate reports based on various filters.

## Features

- **User Authentication**: Users can log in securely using their email and password.
- **Dashboard**: Provides an overview of debts and credits, displaying the total amount you owe and are owed.
- **Add Expense**: Users can add new expenses, specifying the item, amount, and participants. The app will automatically update the balances.
- **Reports**: Generate reports based on various filters such as search query, month, year, and paid by.
- **Delete Logs**: Users can delete specific expense logs, and the app will adjust the balances accordingly.

## Technologies Used

- **Flask**: Web framework for building the application.
- **Pyrebase**: Python wrapper for the Firebase Realtime Database.
- **Firebase Authentication**: Used for user authentication.
- **HTML/CSS**: Front-end design and layout.
- **Bootstrap**: Front-end framework for responsive design.

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your_username/expense-tracker.git

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
  
3.  **Set up Firebase:**
    -   Create a new project on the [Firebase Console](https://console.firebase.google.com/).
    -   Obtain the configuration settings and set them as environment variables in your local environment or update the `config` dictionary in `app.py` with your Firebase project details.
4.  **Set the Flask secret key:**
    
    -   Set the `app.secret_key` in `app.py` to a secure random string.
5.  **Run the application:**
    ```bash
       `python3 app.py` 
 
   The app will be accessible at [http://localhost:8000](http://localhost:8000/).
    

## Environment Variables

Ensure the following environment variables are set:

-   `API_KEY`
-   `AUTH_DOMAIN`
-   `PROJECT_ID`
-   `STORAGE_BUCKET`
-   `MESSAGING_SENDER_ID`
-   `APP_ID`
-   `MEASUREMENT_ID`
-   `DATABASE_URL`

## Usage

1.  Visit [http://localhost:8000](http://localhost:8000/) in your web browser.
2.  Log in with your registered email and password.
3.  Navigate through the dashboard, add expenses, and generate reports as needed.
4.  Log out when finished.
