import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import io
import base64
import re
import time  # Import the time module

# Define a list of user agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    # Add more user agents as needed
]

# Function to get title and year from URL
def get_title_and_year_from_url(url):
    try:
        # Choose a random user agent from the list
        user_agent = random.choice(user_agents)

        # Set the User-Agent header in the request
        headers = {
            'User-Agent': user_agent
        }

        # Send an HTTP GET request to the URL with the selected user agent
        response = requests.get(url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the title tag within the HTML
            title_tag = soup.find('title')

            # Extract the text from the title tag
            if title_tag:
                title = title_tag.text
                # Use regular expressions to extract the year from the title
                year_match = re.search(r'\(\d{4}\)', title)
                if year_match:
                    year = year_match.group()
                else:
                    year = "Year not found"
                return title, year
            else:
                # If title tag is not found, find the h1 tag
                h1_tag = soup.find('h1')
                if h1_tag:
                    title = h1_tag.text
                    # Use regular expressions to extract the year from the title
                    year_match = re.search(r'\(\d{4}\)', title)
                    if year_match:
                        year = year_match.group()
                    else:
                        year = "Year not found"
                    return title, year
                else:
                    return "Title not found", "Year not found"
        else:
            return f'Failed to retrieve the web page from {url}.', "Year not found"
    except Exception as e:
        return f'An error occurred while processing {url}: {str(e)}', "Year not found"

# Streamlit UI
st.title("Web Title Scraper")

# Create a radio button to select download format
download_format = st.radio("Select download format:", ["CSV", "HTML"])

# User input for URLs
st.write("Enter the URLs you want to scrape (separated by line breaks):")
user_input = st.text_area("Input URLs", "")

# Process user input and display titles
if st.button("Scrape Titles"):
    urls = user_input.split("\n")
    results = []

    # Create a progress bar using st.empty()
    progress_bar = st.empty()

    for i, url in enumerate(urls):
        title, year = get_title_and_year_from_url(url.strip())
        results.append({'URL': url, 'Title': title, 'Year': year})

        # Update the progress bar visually
        progress_percent = (i + 1) / len(urls) * 100
        progress_bar.text(f"Progress: {progress_percent:.2f}%")

    # Create a DataFrame from the results
    df = pd.DataFrame(results)

    # Display the DataFrame
    st.write(df)

    # Display the execution count and final progress as text
    st.text(f"Processed: {len(urls)} URLs")
    st.text(f"Progress: 100.00%")

    if download_format:
        if download_format == "CSV":
            # Save the DataFrame to a CSV file
            csv_data = df.to_csv(index=False)
            b64 = base64.b64encode(csv_data.encode()).decode()
            st.markdown(
                f'<a href="data:file/csv;base64,{b64}" download="scraped_titles.csv">Download CSV</a>',
                unsafe_allow_html=True
            )
        elif download_format == "HTML":
            # Save the DataFrame to an HTML file
            html_data = df.to_html(index=False)
            b64 = base64.b64encode(html_data.encode()).decode()
            st.markdown(
                f'<a href="data:file/html;base64,{b64}" download="scraped_titles.html">Download HTML</a>',
                unsafe_allow_html=True
            )
