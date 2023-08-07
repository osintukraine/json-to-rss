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

            return sanitized_url
        except UnicodeDecodeError:
            return "Error: Unicode decode error"
        except AttributeError:
            return "Error: Attribute decode error"
    else:
        return encoded_url


def sanitize_value(value):
    if isinstance(value, str):
        # Remove non-printable characters from the string
        sanitized_value = ''.join(char for char in value if unicodedata.category(char)[0] != 'C')
        return sanitized_value
    else:
        return value

def dict_to_xml(dictionary, parent=None, skip_keys=None):
    if parent is None:
        parent = ET.Element('root')

    if skip_keys is None:
        skip_keys = ['content_html', 'id']

    if isinstance(dictionary, dict):
        for key, value in dictionary.items():
            if key in skip_keys:
                continue

            if isinstance(value, dict):
                element = ET.SubElement(parent, key)
                dict_to_xml(value, parent=element, skip_keys=skip_keys)
            elif isinstance(value, list):
                for item in value:
                    element = ET.SubElement(parent, key)
                    dict_to_xml(item, parent=element, skip_keys=skip_keys)
            else:
                # Change 'url' to 'link' when creating an XML element
                element_key = 'link' if key == 'url' else key
                element = ET.SubElement(parent, element_key)
                if key == 'url':
                    # Split URL string on null character and decode only the first part
                    split_url = value.split('\x01', 1)
                    decoded_url = decode_url(split_url[0])
                    element.text = decoded_url
                else:
                    element.text = str(value)
    elif isinstance(dictionary, list):
        for item in dictionary:
            element = ET.SubElement(parent, 'item')
            dict_to_xml(item, parent=element, skip_keys=skip_keys)
    else:
        parent.text = str(dictionary)

    return parent




def write_xml_to_file(xml_element, filename):
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


# Fetch JSON data from the URL
json_feed_url = input("Please enter the JSON feed URL: ")
json_data = fetch_json_data(json_feed_url)

if json_data:
    # Convert JSON to XML
    xml_root = dict_to_xml(json_data)

    # Write XML to file
    write_xml_to_file(xml_root, 'feed.xml')
    print("XML file generated successfully.")