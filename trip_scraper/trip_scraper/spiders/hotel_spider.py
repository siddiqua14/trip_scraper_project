import scrapy
import json
import re

class HotelsSpider(scrapy.Spider):
    name = "hotels"
    start_urls = [
        "https://uk.trip.com/hotels/?locale=en-GB&curr=GBP"
    ]

    def parse(self, response):
        # Search for the window.IBU_HOTEL object in <script> tags using a regular expression
        script_data = response.xpath(
            '//script[contains(text(), "window.IBU_HOTEL")]/text()'
        ).get()

        if not script_data:
            self.logger.error("No script containing 'window.IBU_HOTEL' found!")
            return

        # Debugging: Log the first part of the script data for inspection
        self.logger.info(f"Script Data Found: {script_data[:500]}")

        # Use regular expressions to extract the entire window.IBU_HOTEL object as JSON
        match = re.search(r'window\.IBU_HOTEL\s*=\s*(\{.*?\});', script_data, re.DOTALL)

        if match:
            try:
                # Extract the JSON part from the match
                json_data = match.group(1)

                # Parse the JSON data
                data = json.loads(json_data)

                # Extract 'htlsData' data from 'initData'
                htls_data = data.get("initData", {}).get("htlsData", {})

                # Check if htlsData contains any data and iterate over it
                if htls_data:
                    # Debugging: Log the first 500 characters of htlsData to verify
                    self.logger.info(f"htlsData: {json.dumps(htls_data, indent=2)[:500]}")

                    # Yield all data from htlsData
                    yield {
                        "htlsData": htls_data
                    }

                else:
                    self.logger.error("No 'htlsData' found in 'initData'.")

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode JSON: {e}")
            except Exception as e:
                self.logger.error(f"An unexpected error occurred: {e}")
        else:
            self.logger.error("Could not match the window.IBU_HOTEL object in the script.")
