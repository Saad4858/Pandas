import requests
from bs4 import BeautifulSoup
import json

# Function to fetch and parse a webpage
cities = []
links = []

def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to retrieve {url}. Status code: {response.status_code}")
        return None

# Function to extract city names and links from the table
def extract_city_links(soup):
    table = soup.find('table', {'id': 'ctl00_cphPage_commoditiesList'})
    if not table:
        print("Failed to find the table with id 'ctl00_cphPage_commoditiesList'.")
        return

    city_links = {}
    for row in table.find_all('tr'):
        tds = row.find_all('td')
        for td in tds:
            link_tag = td.find('a', href=True)
            if link_tag and 'commodityId' in link_tag['href']:
                city_name = link_tag.text.strip()
                link = link_tag['href']
                city_links[city_name] = link
                
                cities.append(city_name)
                links.append(link)

    return city_links


# Main URL
url = 'http://www.amis.pk/BrowsePrices.aspx?searchType=1'

# Fetch the main page
soup = fetch_page(url)

city_links = []

if soup:
    # Extract city names and links from the table
    city_links = extract_city_links(soup)
    if city_links:
        # Convert the data to JSON format
        city_links_json = json.dumps(city_links, indent=4)


# Function to fetch and parse a webpage
def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to retrieve {url}. Status code: {response.status_code}")
        return None

# Function to extract price data from the table within a specific div
def extract_price_data(soup):
    div = soup.find('div', {'id': 'amis_prices'})
    if not div:
        print("Failed to find the div with id 'amis_prices' in the page.")
        return

    table = div.find('table', {'class': 'cart'})
    if not table:
        print("Failed to find the table within the div.")
        return

    data = []
    headers = ['Crop', 'Min', 'Max', 'FQP']

    for row in table.find_all('tr')[1:]:  # Skip the header row
        th = row.find('th', {'class': 'listItem'})
        columns = row.find_all('td')
        if th and columns:
            crop = th.find('a').text.strip() if th.find('a') else th.text.strip()
            min_price = columns[1].text.strip()  # The second td for Min price
            max_price = columns[2].text.strip()  # The third td for Max price
            fqp = columns[3].text.strip()  # The fourth td for FQP price
            row_data = {
                'Crop': crop,
                'Min': min_price,
                'Max': max_price,
                'FQP': fqp
            }
            data.append(row_data)

    return data


# Fetch the main page
cities_data = {}

for i, link in enumerate(links):
    link = "http://www.amis.pk/" + link
    soup = fetch_page(link)

    if soup:
        # Extract price data from the table within the specific div
        price_data = extract_price_data(soup)
        if price_data:
            # Convert the data to JSON format
            cities_data[cities[i]] = price_data

# Saving as JSON
with open('cities_crop_prices.json', 'w') as json_file:
    json.dump(cities_data, json_file, indent=4)