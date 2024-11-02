import requests
from bs4 import BeautifulSoup
import json

def extract_images(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    images = []

    image_div = soup.find('div', id='main-image-container')
    if image_div:
        ul = image_div.find('ul')
        if ul:
            img_tags = ul.find_all('img')
            for img in img_tags:
                if 'src' in img.attrs:
                    images.append(img['src'])
    return images

def extract_title(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('span', id='productTitle')
    if title:
        full_title = title.text.strip()
        short_title = full_title.split(',')[0]
        return short_title

    
def extract_colors(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    colors = []

    color_div = soup.find('div', id="variation_color_name")
    if color_div:
        ul = color_div.find('ul')
        if ul:
            img_tags = ul.find_all('img')
            for img in img_tags:
                if 'alt' in img.attrs:
                    colors.append(img['alt'])
    return colors

def extract_sizes(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    sizes = []

    color_div = soup.find('div', id="variation_size_name")
    if color_div:
        ul = color_div.find('ul')
        if ul:
            img_tags = ul.find_all('p')
            for p in img_tags:
                sizes.append(p.text.strip())
    return sizes

def extract_description(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    details = {}

    div = soup.find('div', id="productOverview_feature_div")
    if div:
        table = div.find('table')
#     else:
#         table = ""

#     return table
# response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
        if table:
            rows = table.find_all('tr', class_='a-spacing-small')
            for row in rows:
                th = row.find('td', class_='a-span3')
                td = row.find('td', class_='a-span9')
                if th and td:
                    key = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    details[key] = value

    return details

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extracting images
    images = extract_images(url)
    
    # Example for extracting selectable options (colors, sizes, etc.)
    options = {}
    option_divs = soup.find_all('div', class_='a-row')
    for div in option_divs:
        label = div.find('span', class_='a-declarative')
        if label:
            option_name = label.text.strip()
            option_values = [value.text.strip() for value in div.find_all('span', class_='a-text-bold')]
            options[option_name] = option_values
    
    # Example for extracting price
    first_price = None
    price_span = soup.find('span', class_='a-price-whole')
    if price_span:
        first_price = price_span.text.strip()
    
    data = {
        "images": images,
        "options": options,
        "price": first_price
    }
    
    # Save to JSON file
    with open('scraper.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    return data
