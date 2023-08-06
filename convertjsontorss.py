import json
import xml.etree.ElementTree as ET
import requests
import base64
import re
from urllib.parse import urlparse

def fetch_json_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch JSON data from {url}.")
        return None

def decode_url(encoded_url):
    if '/articles/' in encoded_url:
        encoded_str = encoded_url.split('/articles/')[1]
        if '?oc=5' in encoded_str:
            encoded_str = encoded_str.split('?oc=5')[0]
        padding = 4 - len(encoded_str) % 4
        encoded_str += "=" * padding
        try:
            decoded_bytes = base64.urlsafe_b64decode(encoded_str)
            decoded_str = decoded_bytes.decode('utf-8', 'ignore')
            # Use urllib.parse to extract the URL from the decoded string
            decoded_url = urlparse(decoded_str).geturl()
        except UnicodeDecodeError:
            decoded_url = "Error: Unicode decode error"
        except AttributeError:
            decoded_url = "Error: Attribute decode error"
    else:
        decoded_url = encoded_url

    return decoded_url

def dict_to_xml(dictionary, parent=None):
    if parent is None:
        parent = ET.Element('root')

    if isinstance(dictionary, dict):
        for key, value in dictionary.items():
            if key == "content_html":  # Skip the "content_html" key
                continue

            if isinstance(value, dict):
                element = ET.SubElement(parent, key)
                dict_to_xml(value, parent=element)
            elif isinstance(value, list):
                for item in value:
                    element = ET.SubElement(parent, key)
                    dict_to_xml(item, parent=element)
            else:
                if key == 'URL':
                    decoded_url = decode_url(value)
                    element = ET.SubElement(parent, key)
                    element.text = decoded_url
                else:
                    element = ET.SubElement(parent, key)
                    element.text = str(value)
    elif isinstance(dictionary, list):
        for item in dictionary:
            element = ET.SubElement(parent, 'item')
            dict_to_xml(item, parent=element)
    else:
        parent.text = str(dictionary)

    return parent


def write_xml_to_file(xml_element, filename):
    with open(filename, 'wb') as file:
        tree = ET.ElementTree(xml_element)
        tree.write(file, encoding='utf-8', xml_declaration=True)

def update_decoded_urls(element):
    for child in element:
        update_decoded_urls(child)

    if element.tag == 'URL':
        decoded_url = decode_url(element.text)
        element.text = decoded_url

# URL for the live JSON feed
json_feed_url = "https://www.inoreader.com/stream/user/1005324229/tag/Ukraine/view/json"

# Fetch JSON data from the URL
json_data = fetch_json_data(json_feed_url)

if json_data:
    # Convert JSON to XML
    xml_root = dict_to_xml(json_data)

    # Write XML to file
    write_xml_to_file(xml_root, 'feed.xml')
    print("XML file generated successfully.")
