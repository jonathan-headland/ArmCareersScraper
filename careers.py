import requests

from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

base_url = 'https://careers.arm.com'
search_url = base_url + '/search-jobs'
page_count = 0
count = 0

response = requests.get(search_url)
soup = BeautifulSoup(response.content, 'html.parser')

search_filters = soup.find(id='search-filters')
selectors = search_filters.select("section", class_="expandable")
for selector in selectors:
    headings = selector.select("h2")
    for heading in headings:
        if heading.text == "filter by city":
            cities = selector.select("input", class_="filter-checkbox")
            for city in cities:
                if city['data-display'].startswith("Cambridge"):
                    job_limit = int(city['data-count'])
                    print(city['data-display'], "has", job_limit)

while count < job_limit:
    page_count += 1
    place_on_page = 0
    response = requests.get(search_url, params = {"p": str(page_count)})
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find(class_='search-results-list')
    for item in results.select('li'):
        place_on_page += 1
        location = item.find(class_='job-location')
        if location.text.startswith('Cambridge') or location.text.startswith('Multiple'):
            title = item.find('h2')
            link = item.find('a')
            job_details = requests.get(base_url + link['href'])
            job_soup = BeautifulSoup(job_details.content, 'html.parser')
            the_id = job_soup.find(class_='job-id')
            id_data = the_id.find(class_='job-info--data')
            the_date = job_soup.find(class_='job-date')
            the_location = job_soup.find(class_="job-info--location")
            location_text = 'unknown'

            if id_data == None: # Older format page
                id_data_text = the_id.text
                date_text = the_date.text
                job_date = datetime.strptime(date_text, '%m/%d/%Y')
                location_data = job_soup.find(class_='ajd_header__location')
            else:
                id_data_text = id_data.text
                date_data = the_date.find(class_='job-info--data')
                date_text = date_data.text
                job_date = datetime.strptime(date_text, '%b. %d, %Y')
                location_data = the_location.find(class_='job-info--data')

            location_text = location_data.text;
            if "Cambridge" in location_text:
                count += 1
                print("{0:2}".format(page_count), "{0:2}".format(place_on_page), "{0:10}".format(id_data_text), title.text, job_date)

print("Total:", count)

