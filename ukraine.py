import json
import xml.etree.ElementTree as ET
import requests
import base64
import re
import os
import unicodedata
from urllib.parse import urlparse
import logging
from xml.dom import minidom
import io


logging.basicConfig(level=logging.INFO)

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

            # Split the decoded URL on the null character and return only the first part
            split_url = decoded_url.split('\x01', 1)

            # Remove non-printable characters from the URL
            sanitized_url = ''.join(char for char in split_url[0] if unicodedata.category(char)[0] != 'C')

            # Find the index of 'https://' and take the substring from that index
            idx = sanitized_url.find('https://')
            if idx != -1:
                sanitized_url = sanitized_url[idx:]

            return sanitized_url
        except UnicodeDecodeError:
            return "Error: Unicode decode error"
        except AttributeError:
            return "Error: Attribute decode error"
    else:
        return encoded_url


def sanitize_value(value):
    """Sanitizes a string value by removing non-printable characters."""
    if isinstance(value, str):
        # Remove non-printable characters from the string
        sanitized_value = ''.join(char for char in value if unicodedata.category(char)[0] != 'C')
        return sanitized_value
    else:
        return value

def sanitize_links(link_text):
    """
    Sanitizes the provided link text by removing any unexpected character
    right before the "https://" portion.
    """
    if not link_text.startswith("http"):
        # Find the position of "https://" in the string
        https_pos = link_text.find("https://")
        if https_pos > 0:
            # Remove any character just before "https://"
            return link_text[https_pos:]
    return link_text


def inspect_and_convert_value(value):
    """Inspects the value and converts it to a string if it's not a string."""
    # If value is a list, print it for inspection
    if isinstance(value, list):
        print(f"Found list value: {value}")
    return str(value)

# Refined dict_to_xml_rss_corrected function without the encoded URL

def dict_to_xml_rss_refined(dictionary, home_page_url, parent=None):
    if parent is None:
        parent = ET.Element('rss', version="2.0")
        channel = ET.SubElement(parent, 'channel')
    else:
        channel = parent

    # Set the main feed attributes
    element = ET.SubElement(channel, 'title')
    element.text = sanitize_value(dictionary.get('title', ''))
    
    element = ET.SubElement(channel, 'link')
    element.text = sanitize_links(home_page_url)
    
    element = ET.SubElement(channel, 'description')
    element.text = sanitize_value(dictionary.get('description', ''))

    # Handle items
    for item_data in dictionary.get('items', []):
        item = ET.SubElement(channel, 'item')
        
        # Extract title and published_date attributes from each item
        for key in ['title', 'published_date']:
            if key in item_data:
                sub_element = ET.SubElement(item, key)
                sub_element.text = sanitize_value(item_data[key])
        
        # Handle decoded URL as <link>
        if 'url' in item_data:
            sub_element = ET.SubElement(item, 'link')
            sub_element.text = decode_url(item_data['url'])

    return parent

# Display the refined function
dict_to_xml_rss_refined



def write_xml_to_file(xml_element, filename):
    # Debugging logic: Check for elements with list as text
    for elem in xml_element.iter():
        if isinstance(elem.text, list):
            print(f"Element '{elem.tag}' has a list as its text: {elem.text}")
    # Log the XML content before writing it to the file
    xml_str = ET.tostring(xml_element, encoding='utf-8').decode('utf-8')
    logging.info(f"XML content:\\n{xml_str}")

    if os.path.exists(filename):
        # Load the existing XML file
        try:
            with open(filename, 'r') as existing_file:
                existing_xml = existing_file.read()

            # Clean up the existing XML file using minidom
            parsed_xml = minidom.parseString(existing_xml)
            cleaned_xml = parsed_xml.toprettyxml(indent="    ")

            # Remove any invalid characters from the cleaned XML
            cleaned_xml = ''.join(char for char in cleaned_xml if unicodedata.category(char)[0] != 'C')

            # Update the existing XML with cleaned version
            with open(filename, 'wb') as file:
                file.write(cleaned_xml.encode('utf-8'))
            print("XML file updated successfully.")
        except Exception as e:
            logging.error(f"Error parsing existing XML file: {e}")
    else:
        # If the file doesn't exist, write the entire XML
        with io.BytesIO() as xml_buffer:
            tree = ET.ElementTree(xml_element)
            tree.write(xml_buffer, encoding='utf-8', xml_declaration=True)
            with open(filename, 'wb') as file:
                file.write(xml_buffer.getvalue())
        print("New XML file generated successfully.")


# URL for the live JSON feed
json_feed_url = "https://www.inoreader.com/stream/user/1005324229/tag/Ukraine/view/json"

# Fetch JSON data from the URL
json_data = fetch_json_data(json_feed_url)
print(f"JSON data fetched: {bool(json_data)}")

# Derive home_page_url from json_feed_url
home_page_url = json_feed_url.replace("/view/json", "/view/html")


if json_data:
    # Convert JSON to XML
    xml_root = dict_to_xml_rss_refined(json_data, home_page_url)

if xml_root:
    print("XML root generated successfully.")

    # Write XML to file
    write_xml_to_file(xml_root, 'feed.xml')
    print("XML file generated successfully.")
