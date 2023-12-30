# MongoDB (NoSQL) Shopping Application and Evaluator
This repository contains a shopping application (shopping_application.py) implemented in Python, utilizing MongoDB as the 
backend database. Additionally, there is an evaluator script (evaluator.py) designed to replicate the concurrent 
functionality of an online e-commerce platform and assess the system's behavior under concurrent operations.

## Prerequisites
 - Python
 - MongoDB

## Setup
 - Install the required packages:

    ```bash
    pip install pymongo
    ```
 - Ensure that MongoDB is running locally on the default port (27017).

## Usage
### Shopping Application
The shopping application provides functionalities such as creating accounts, submitting orders, posting reviews, adding 
products, updating stock levels, and retrieving product information.

### Shopping Evaluator
The evaluator script initializes the shopping database with random data and runs multiple threads to simulate concurrent
user interactions. It measures metrics such as the percentage of products with stock levels less than zero and the total
number of operations.

 - Run the application:
    ```bash
    python shopping_application.py
    ```
\
Feel free to explore, modify, and extend the application and evaluator based on your requirements.