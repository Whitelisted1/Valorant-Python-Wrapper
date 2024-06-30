from typing import Generator, Callable, Any
import re


class XMLParser:
    def __init__(self):
        self.buffer = ""

    def custom_checks(self, xml_data: str) -> bool:
        return xml_data.startswith("<?xml") or xml_data.startswith("<stream:features>") or xml_data.startswith("<message")

    def parse_xml(self, xml_data: str) -> list:
        """
        Parses the XML data from a stream. Returns a list of the parsed XML data once it has been completely been received

        Parameters:
        xml_data (str): The XML data to parse

        Returns:
        list: A list of parsed XMl data
        """

        # add the buffer to the new data, then clear the buffer
        xml_data = self.buffer + xml_data
        self.buffer = ""

        # if the xml data passes our custom checks function, instantly return it
        if self.custom_checks(xml_data):
            return [xml_data]

        # find the starting tag
        start_tag = re.findall(r'<(\w+)', xml_data)

        # if we couldn't find the starting tag, we add the data to the buffer and cancel
        if len(start_tag) == 0:
            self.buffer = xml_data
            return []

        # get the starting tag and the length of the starting tag
        start_tag = start_tag[0]
        # start_tag_length = xml_data.index(">")
        start_tag_length = len(start_tag)

        # find the stoppping tag, if it exists
        stop_tag = xml_data.find(f"</{start_tag}")

        # if we couldn't find the stopping tag, we add the data to the buffer and cancel
        if stop_tag == -1:
            self.buffer = xml_data
            return []

        # do a check to see if there is more data on the end of this xml file
        if len(xml_data) <= stop_tag + start_tag_length + 3:
            # if not, then we return the xml data
            return [xml_data]

        # get the xml file that is recognized by the start_tag and stop_tag checks
        newest_xml = xml_data[:stop_tag + start_tag_length + 3]

        # recursively search the rest of this data to see if there are any other xml files
        search_output = self.parse_xml(xml_data[len(newest_xml):])

        # put the first xml data in front of the other xml data
        return [newest_xml] + search_output

    def parse_stream(self, generator: Generator[str, None, None], callback: Callable[[str], Any]) -> None:
        """
        Parses the XML data from the Generator object and calls the callback when an XML object is found

        Parameters:
        generator (Generator[str, None, None]): The generator object. Expected to yield string output.
        callback (Callable[[str], Any]): The callback object. Is called with the parser output as a string.
        """

        for data in generator:
            parser_output = self.parse_xml(data)

            if len(parser_output) == 0:
                continue

            callback(parser_output)
