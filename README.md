# json-to-rss
Parse a JSON feed with Google News URL's, base64 decode them and replace the URL with final target

This code performs the following steps:

    Import necessary libraries/modules:
        json: To work with JSON data.
        xml.etree.ElementTree as ET: To work with XML data.
        requests: To make HTTP requests and fetch JSON data from a URL.
        base64: To decode Base64-encoded data.
        re: To work with regular expressions.
        urlparse from urllib.parse: To extract the URL from a decoded string.

    Define the fetch_json_data function:
        This function takes a URL as input.
        It makes a GET request to the provided URL using the requests.get method.
        If the response status code is 200 (OK), it returns the JSON data using response.json().
        If the response status code is not 200, it prints an error message and returns None.

    Define the decode_url function:
        This function takes a Base64-encoded URL as input.
        It checks if the URL contains '/articles/' and if so, extracts the encoded part after it.
        If the URL contains '?oc=5', it removes it from the encoded string.
        It ensures that the encoded string has proper padding (a multiple of 4 characters).
        It attempts to decode the URL using base64.urlsafe_b64decode.
        If successful, it then decodes the bytes to a UTF-8 string.
        Finally, it uses urllib.parse.urlparse to extract the URL from the decoded string.
        If any decoding errors occur, appropriate error messages are returned.

    Define the dict_to_xml function:
        This function converts a nested dictionary to an XML element structure.
        It takes the dictionary and an optional parent XML element as input.
        It recursively traverses the dictionary and creates XML elements for each key-value pair.
        It handles dictionaries, lists, and other data types appropriately.

    Define the write_xml_to_file function:
        This function takes an XML element and a filename as input.
        It writes the XML element to the specified file in UTF-8 encoding with XML declaration.

    Define the update_decoded_urls function:
        This function is used to update URL elements in the XML tree with their decoded versions.
        It recursively traverses the XML tree and decodes URL elements using the decode_url function.

    Set the json_feed_url variable with the URL for the live JSON feed.

    Fetch JSON data from the provided URL using the fetch_json_data function and store it in the json_data variable.

    If JSON data is fetched successfully (not None), proceed with the conversion and writing to XML:
        Convert the JSON data to an XML root element using the dict_to_xml function.
        Write the XML root element to a file named "feed.xml" using the write_xml_to_file function.
        Print "XML file generated successfully" indicating successful completion of the XML generation and writing process.
