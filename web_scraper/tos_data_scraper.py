"""
This script logs into the ToS;DR website and scrapes links to terms of services 
across multiple pages, saving the links to a CSV file.
"""

import requests
from bs4 import BeautifulSoup
import logging
import csv
import time

# Constants for base URLs and endpoints
BASE_URL = 'https://edit.tosdr.org'
LOGIN_URL = f"{BASE_URL}/users/sign_in"
SERVICES_URL = f"{BASE_URL}/services"
DELAY = 5
TOTAL_PAGES = 328

# Setting up logging
logging.basicConfig(level=logging.INFO)

def fetch_csrf_token(session):
    """
    Fetch the CSRF token from the login page.
    
    Args:
    - session (requests.Session): Active session object
    
    Returns:
    - str: CSRF token value or None if not found
    """
    response = session.get(LOGIN_URL)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    token_input = soup.find('input', {'name': 'authenticity_token'})
    
    if not token_input:
        logging.error("Failed to retrieve CSRF token.")
        return None

    return token_input['value']

def login(session, email, password):
    """
    Login to the website using the provided credentials.
    
    Args:
    - session (requests.Session): Active session object
    - email (str): User's email
    - password (str): User's password
    
    Returns:
    - bool: True if login was successful, False otherwise
    """
    csrf_token = fetch_csrf_token(session)
    if not csrf_token:
        return False

    payload = {
        'user[email]': email,
        'user[password]': password,
        'authenticity_token': csrf_token
    }

    response = session.post(LOGIN_URL, data=payload)
    if response.status_code != 200:
        logging.error("Login failed with status code %s.", response.status_code)
        return False

    return True

def scrape_page(session, page_number):
    """
    Scrape ToS links from a specified page.
    
    Args:
    - session (requests.Session): Active session object
    - page_number (int): Page number to scrape
    
    Returns:
    - list: List of scraped ToS links
    """
    # Construct the appropriate URL based on page number
    page_url = SERVICES_URL
    if page_number > 1:
        page_url += f"?page={page_number}"
    
    response = session.get(page_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr', class_='toSort')
    
    links = []
    for row in rows:
        link_elem = row.find('td', class_='text-right').a
        if link_elem:
            links.append(BASE_URL + link_elem['href'])
    
    time.sleep(DELAY)
    return links

def main():
    """
    Main script execution function.
    """
    # TODO: Replace with environment variables or secure config fetch
    email = "YOUR_EMAIL"
    password = "YOUR_PASSWORD"

    tos_links = []
    with requests.Session() as session:
        if not login(session, email, password):
            logging.error("Login failed. Exiting.")
            return
        
        # Scrape all pages for ToS links
        for page in range(1, TOTAL_PAGES + 1):
            tos_links.extend(scrape_page(session, page))

    # Save the scraped links to a CSV file
    filename = "tos_links.csv"
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ToS Links"])
        for link in tos_links:
            writer.writerow([link])

    logging.info(f"Links saved to {filename}")

if __name__ == "__main__":
    main()