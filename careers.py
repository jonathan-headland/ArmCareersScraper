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

page_total_message = soup.find(class_='pagination-total-pages')
page_total_string = page_total_message.text.split("of ")[1]
page_total = int(page_total_string)
print("Number of pages:", page_total)

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

job_list = []
while count < job_limit and page_count < page_total:
    page_count += 1
    place_on_page = 0
    print("Processing page:", page_count)
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
                #print("{0:2}".format(page_count), "{0:2}".format(place_on_page), "{0:10}".format(id_data_text), title.text, job_date)
                the_job = {
                        "date":  job_date,
                        "page":  page_count,
                        "line":  place_on_page,
                        "id":    id_data_text,
                        "title": title.text
                        }
                job_list.append(the_job)

print("Total found:", len(job_list))

job_list.sort(reverse=False, key=lambda x: x['date'])

for job in job_list:
    date = job["date"]
    page = job["page"]
    line = job["line"]
    identifier = job["id"]
    title = job["title"]
    date_str = date.strftime("%Y-%m-%d")
    print(date_str, "{0:2}".format(page), "{0:2}".format(line), "{0:10}".format(identifier), title)
