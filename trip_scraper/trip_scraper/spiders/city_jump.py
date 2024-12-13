import scrapy
import json
import re

class HotelsSpider(scrapy.Spider):
    name = "city_jump"
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

                # Debugging: Check if 'inboundCities' is present and log the first city
                inbound_cities = htls_data.get("inboundCities", [])
                if inbound_cities:
                    self.logger.info(f"Found {len(inbound_cities)} inbound cities.")

                    for city in inbound_cities:
                        city_id = city.get("id")
                        city_name = city.get("name")

                        if city_id and city_name:
                            hotels_list_url = f"https://uk.trip.com/hotels/list?city={city_id}"
                            self.logger.info(f"City: {city_name}, Hotels List URL: {hotels_list_url}")

                            # Yield the city name and URL for further processing
                            yield {
                                "city_name": city_name,
                                "hotels_list_url": hotels_list_url
                            }
                else:
                    self.logger.error("No 'inboundCities' found in 'htlsData'.")

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode JSON: {e}")
            except Exception as e:
                self.logger.error(f"An unexpected error occurred: {e}")
        else:
            self.logger.error("Could not match the window.IBU_HOTEL object in the script.")