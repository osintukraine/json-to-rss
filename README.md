
# json-to-rss Script Documentation
##  Parse a JSON feed with Google News URL's, base64 decode them and replace the URL with final target
##  This code is designed with Inoreader JSON Link from folders in mind (see ukraine.py) albeit it should/could work with other JSON URLs

## Environment Setup for Ukraine.py Script

1. **System Requirements**: Ensure you are running a Linux-based system.

2. **Python Environment**:
    - Ensure Python 3 is installed: `python3 --version`
    - If not, install Python 3: `sudo apt-get install python3`
    - It's recommended to use a virtual environment: 
        ```
        python3 -m venv myenv
        source myenv/bin/activate
        ```

3. **Required Python Libraries**:
    - A `requirements.txt` file contains all the necessary libraries.
    - Install them using: `pip install -r requirements.txt`
    - Import necessary libraries/modules:
        json: To work with JSON data.
        xml.etree.ElementTree as ET: To work with XML data.
        requests: To make HTTP requests and fetch JSON data from a URL.
        base64: To decode Base64-encoded data.
        re: To work with regular expressions.
        urlparse from urllib.parse: To extract the URL from a decoded string.



## Code Overview

1. **Import Necessary Libraries**:
    - The script starts by importing all the necessary modules and libraries.

2. **Define Utility Functions**:
    - `sanitize_links()`: A helper function that ensures the links do not contain unwanted characters or patterns.
    - `decode_url()`: Handles the decoding of URLs that are encoded in base64 format. It also uses the `sanitize_links()` function to ensure the decoded URLs are clean.
    - `dict_to_xml_rss_refined()`: Converts the JSON data to an XML format that complies with the RSS 2.0 specification. It also uses `decode_url()` to handle encoded URLs.

3. **Fetch JSON Data**:
    - The `fetch_json_data()` function fetches JSON data from the provided URL using the `requests` library.
    - This function takes a URL as input.
        It makes a GET request to the provided URL using the requests.get method.
        If the response status code is 200 (OK), it returns the JSON data using response.json().
        If the response status code is not 200, it prints an error message and returns None.

4. **User Input**:
    - The script prompts the user for the JSON feed URL and the desired name for the XML file.

5. **Define the decode_url function**:
     - This function takes a Base64-encoded URL as input.
        It checks if the URL contains '/articles/' and if so, extracts the encoded part after it.
        If the URL contains '?oc=5', it removes it from the encoded string.
        It ensures that the encoded string has proper padding (a multiple of 4 characters).
        It attempts to decode the URL using base64.urlsafe_b64decode.
        If successful, it then decodes the bytes to a UTF-8 string.
        Finally, it uses urllib.parse.urlparse to extract the URL from the decoded string.
        If any decoding errors occur, appropriate error messages are returned.

        
6. **Convert JSON to XML**:
    - The fetched JSON data is converted to XML using the `dict_to_xml_rss_refined()` function

7. **Log XML Data**:
    - Before writing the XML data to a file, it's logged using Python's `logging` module for debugging purposes.

8. **Write XML to File**:
    - The `write_xml_to_file()` function handles the writing of the XML structure to a file. 
    - If there are any issues with the existing XML file (if it exists), it's cleaned using the `xml.dom.minidom` library. The XML content is then written to the file.

## Usage Instructions

1. Clone the repository or download the script.
2. Set up the environment as described above.
3. Run the script: `python3 ukraine.py`
4. Provide the necessary inputs when prompted: JSON feed URL and the desired name for the XML file.
5. Once the script completes, the XML file will be created in the current directory.


