# FrankRank - Financial Advisory Chatbot
<p align="center">
<img src="images/website.png">
</p>

## Problem

Finances often depend on subjective opinions, influenced by preconceptions or the potential dishonesty of financial advisors, leading individuals to be exposed to excessive risks due to poor advice.

## Solution

FrankRank - Python-based web application that addresses this issue by utilizing a chatbot, specifically ChatGPT. 

FrankRank stands as a Python-based web application designed to revolutionize financial decision-making through the implementation of an objective chatbot powered by ChatGPT. This innovative approach aims to mitigate biases and emotional influences inherent in human decision-making processes related to finances. Application boasts a robustly implemented backend logic akin to ChatGPT, integrating sophisticated CRUD (Create, Read, Update, Delete) functionalities seamlessly orchestrated through Django's powerful ORM (Object-Relational Mapping) framework.

## What did we implement?

- **Prompt Engineering:** OpenAI API is utilized for prompt engineering.
- **Web Development:** We created a website using the Django framework that stores customer data and acts as an interaction intermediary.
- **Stock Analysis Functions:**
    - Determine the company's trend on the stock exchange.
    - Format the latest news on the stock exchange.
    - Display companies' biggest shareholders.
- **Forecast Function:** We developed a function for a forecast of the company's price.
- **Login System:**: Enhances user engagement by tailoring the chat experience based on signup responses. Customers can answer specific questions during signup, thus influencing the chat system's responses for a personalized and intuitive platform
- **Yahoo Finance:** Utilizing Yahoo Finance, we can provide real-time data that can be leveraged by the chat system in accordance with user requirements.
- **Web Scraping:** The application performs web scraping to gather information from financial magazines.

<p align="center">
<img src="images/webgif.gif" alt="Video GIF" width="800" height="450">
</p>

## Backend Overwiev
- **User Authentication and Authorization:**
    - Signup and login views enabling user registration and login with username, email, password, and OpenAI API key.
    - "Login with Google" option for streamlined access using the OpenAI API key.
- **User Settings Customization:**
    - Settings page for user-specific preferences like investments, sectors, risk level, and other parameters to fine-tune the GPT-based advice system.
- **Chat Management:**
    - Categorized chats covering personal finance, investments, insurance, and car insurance.
    - Dropdown menu for users to switch between chat categories.
    - Record of past chats, allowing users to view previous conversations.
    - Access to unique URLs for individual chat sessions for easy retrieval and continuation of discussions.
    - Ability for users to create new chats within the current category for initiating fresh discussions related to the chosen financial aspect.
- **Logout Functionality:**
    - Secure logout to terminate user sessions and maintain account security.
- **Integration with OpenAI API:**
    - Utilization of the OpenAI API to power the chatbot functionality for objective financial advice generation.
- **Backend Navigation and Redirection:**
    - Redirects from signup to settings page for initial customization.
    - Seamless user experience by categorizing and displaying only chats relevant to the selected category.

## Technologies Used

- **Django:** A high-level Python web framework for building robust web applications.
- **OpenAI:** The OpenAI API is employed for fine-tuning ChatGPT and integrating it into the chatbot.
- **Azure Storage Blob:** The application utilizes Azure Storage Blob to store and manage data.
- **Semantic UI / HTML:** Semantic UI and HTML are used for frontend development, ensuring a user-friendly interface.
- **Data Warehousing:** We configured a Data Warehouse (DWH) on Azure SQL to store and manage customer data.

## Getting Started
```sh
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
