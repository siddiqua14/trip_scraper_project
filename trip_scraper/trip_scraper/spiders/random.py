import scrapy
import json
import re
import random

class HotelsSpider(scrapy.Spider):
    name = "random"
    start_urls = [
        "https://uk.trip.com/hotels/?locale=en-GB&curr=GBP"
    ]

    def parse(self, response):
        # Extract the script containing window.IBU_HOTEL using XPath
        script_data = response.xpath(
            '//script[contains(text(), "window.IBU_HOTEL")]/text()'
        ).get()

        if not script_data:
            self.logger.error("No script containing 'window.IBU_HOTEL' found!")
            return

        # Extract the JSON structure using regex
        match = re.search(r'window\.IBU_HOTEL\s*=\s*(\{.*?\});', script_data, re.DOTALL)

        if match:
            try:
                # Load JSON data
                json_data = match.group(1)
                data = json.loads(json_data)

                # Print the entire JSON data for debugging
                self.logger.info("Extracted JSON data: %s", json.dumps(data, indent=2))

                # Extract inboundCities and outboundCities
                inbound_cities = data.get("initData", {}).get("htlsData", {}).get("inboundCities", [])
                outbound_cities = data.get("initData", {}).get("htlsData", {}).get("outboundCities", [])

                # Ensure both lists exist
                if not inbound_cities and not outbound_cities:
                    self.logger.error("No inbound or outbound cities found!")
                    return

                # Randomly choose between inboundCities and outboundCities
                chosen_city_list = random.choice([inbound_cities, outbound_cities])

                # Select a random city from the chosen list
                random_city = random.choice(chosen_city_list)

                # Get city ID and name
                city_id = random_city.get("id")
                city_name = random_city.get("name")

                if not city_id:
                    self.logger.error("City ID not found in the chosen city!")
                    return

                # Construct the new URL for hotel list
                hotels_list_url = f"https://uk.trip.com/hotels/list?city={city_id}"

                # Pass city ID and name to the next parsing function
                yield scrapy.Request(
                    hotels_list_url, 
                    callback=self.parse_hotel_list,
                    meta={'city_id': city_id, 'city_name': city_name}
                )

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode JSON: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
        else:
            self.logger.error("Could not match the window.IBU_HOTEL object in the script.")

    def parse_hotel_list(self, response):
        # Extract the script containing window.IBU_HOTEL from the new page
        script_data = response.xpath(
            '//script[contains(text(), "window.IBU_HOTEL")]/text()'
        ).get()

        if not script_data:
            self.logger.error("No script containing 'window.IBU_HOTEL' found in the hotel list page!")
            return

        # Extract JSON structure using regex
        match = re.search(r'window\.IBU_HOTEL\s*=\s*(\{.*?\});', script_data, re.DOTALL)

        if match:
            try:
                # Load JSON data
                json_data = match.group(1)
                data = json.loads(json_data)

                # Print the entire JSON data for debugging
                self.logger.info("Extracted JSON data from hotel list: %s", json.dumps(data, indent=2))

                # Extract hotelList from firstPageList
                hotel_list = data.get("initData", {}).get("firstPageList", {}).get("hotelList", [])

                if not hotel_list:
                    self.logger.error("No hotels found in the hotel list!")
                    return

                # Get city ID and name from meta data
                city_id = response.meta['city_id']
                city_name = response.meta['city_name']

                # Loop through the hotel list and extract the required information
                for hotel in hotel_list:
                    hotel_basic_info = hotel.get("hotelBasicInfo", {})
                    comment_info = hotel.get("commentInfo", {})
                    room_info = hotel.get("roomInfo", {})
                    position_info = hotel.get("positionInfo", {})
                    coordinate = position_info.get("coordinate", {})

                    # Extract data from each hotel
                    hotel_data = {
                        "city_id": city_id,
                        "city_name": city_name,
                        "hotel_id": hotel_basic_info.get("hotelId"),  # Added hotel ID here
                        "hotelName": hotel_basic_info.get("hotelName"),
                        "commentScore": comment_info.get("commentScore"),
                        "positionName": position_info.get("positionName"),
                        "latitude": coordinate.get("lat"),
                        "longitude": coordinate.get("lng"),
                        "roomType": room_info.get("physicalRoomName"),
                        "price": hotel_basic_info.get("price"),
                        "hotelImg": hotel_basic_info.get("hotelImg")
                    }

                    # Print the extracted hotel data for debugging purposes
                    self.logger.info("Extracted hotel data: %s", json.dumps(hotel_data, indent=2))

                    # Yield the data if it's not empty
                    if any(value is not None for value in hotel_data.values()):
                        yield hotel_data

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode JSON: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
        else:
            self.logger.error("Could not match the window.IBU_HOTEL object in the script.")
