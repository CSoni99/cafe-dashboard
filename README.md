# Cafe Marketing Dashboard

A simple, user-friendly dashboard to monitor your Meta (Facebook/Instagram) marketing campaigns for your Cafe.

## Prerequisites

1.  **Python 3.10+** installed on your system.
2.  **API Tokens**: This project is pre-configured with the necessary API tokens in `.streamlit/secrets.toml`. Do not share this file publicly.

## Installation

1.  Open your terminal/command prompt.
2.  Navigate to this folder.
3.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```
4.  Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Dashboard

1.  Run the following command:
    ```bash
    streamlit run app.py
    ```
2.  A new browser tab will open automatically showing your dashboard.
3.  Select your **Ad Account** from the sidebar.
4.  View your active campaigns and their performance!

## Features

-   **Simple Overview**: See total Money Spent, People Reached, and Views.
-   **Campaign Details**: Select specific campaigns to see how they are performing.
-   **Visuals**: Easy-to-understand charts.
