import asyncio
import csv
import http.client
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from os import getenv
from typing import List, Optional

import aiohttp
import httpx
from dotenv import load_dotenv

from src.exceptions.exceptions import GeocodeError
from src.schemas.geocode import BatchGeocodeResponse, Location
from src.utils.utils import haversine_distance, sort_location_by_distance

load_dotenv()


class GeocodeClass:
    def __init__(self):
        self.auth = getenv("AUTH_KEY")

    def get_coordinates_for_destination(self, location: str, user_lat: float, user_lon: float):
        conn = http.client.HTTPSConnection("geocode.xyz")

        # cleaned_location = location.strip()
        # sanetized_location = cleaned_location.split()
        # main_location, city, region = sanetized_location[0], sanetized_location[1], sanetized_location[2] 

        payload = {
            "auth": self.auth,
            "locate": f"{location}, Kumasi, Ghana",
            # "region": "GH",
            "json": 1,
            "moreinfo": 1
        }
        params = urllib.parse.urlencode(payload)

        try:
            conn.request("GET", f'/?{params}')
            res = conn.getresponse()

            if res.status != 200:
                raise GeocodeError("Could not connect to geocode service")
            
            response = res.read()

            data = json.loads(response.decode("utf-8"))

            longitude = float(data["longt"]) 
            latitude = float(data["latt"])

            if longitude == 0.0 and latitude == 0.0:
                raise GeocodeError(
                    f"No valid coordinates returned for the location {location}. Try adding a city or country separated by comma"
                )
            
            # distance = haversine_distance(5.5545, -0.1902, latitude, longitude)
            distance = haversine_distance(user_lat, user_lon, latitude, longitude)
            
            return {
                "location": location,
                "longitude": longitude,
                "latitude": latitude,
                "status": "success"
            }
        except Exception as e:
            raise GeocodeError(str(e))



    async def get_coordinates_async_aiohttp(
            self,
            location: str,
            session: aiohttp.ClientSession
    ):
        url = "geocode.xyz"
        params = {
            "auth": self.auth,
            "locate": location,
            # "region": "Ghana",
            "json": 1   
        }

        try:
            async with session.get(url, params=params) as response:
                if response != 200:
                    raise GeocodeError(f"HTTP {response.status}: Could not connect to geocode service")
                
                data = await response.json()
                longitude = float(data["longt"])
                latitude = float(data["latt"])

                if longitude == 0.0 and latitude == 0.0:
                    raise GeocodeError(f"No valid coordinates returned for location {location}")
                
                distance = haversine_distance(5.5545, -0.1902, latitude, longitude)
                
                return {
                    "location": location,
                    "longitude": longitude,
                    "latitude": latitude,
                    "status": "success"
                }
        except Exception as e:
            return {
                "location": location,
                "longitude": None,
                "latitude": None,
                "status": "error",
                "error": str(e)
            }


    # @staticmethod
    async def geocode_with_thread_pool(
        self,
        locations: List[str],
        user_lat: float,
        user_lon: float,
        max_retries_per_location: int = 1 
    ):
        async def geocode_single_retry(location: str):
            last_exception = None

            for attempt in range(max_retries_per_location + 1):
                try:
                    if attempt > 0:
                        await asyncio.sleep(0.5*attempt)

                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor(max_workers=5) as executor:
                        result = await loop.run_in_executor(
                            executor,
                            self.get_coordinates_for_destination,
                            location, user_lat, user_lon
                        )
                    return {"success": True, "result": result, "location": location}
                
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries_per_location:
                        print(f"Retry {attempt + 1} for {location}: {e}")
                        continue
            
            return {"success": False, "error": str(last_exception), "location": location}
        
        tasks = [
            geocode_single_retry(location) for location in locations
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        failed = []

        # for location, response in zip(locations, responses):
        #     if isinstance(response, Exception):
        #         print(f"Failed to geocode {location}: {response}")
        #         failed.append(location)
        #     else:
        #         results.append(response)
        for response in responses:
            if response["success"]:
                print("Response[result]: ", response["result"])
                results.append(response["result"])
            else:
                print(f"Failed to geocode {response["location"]} after retries: {response["error"]}")
                failed.append(response["location"]) 
            
        # sorted_results = sort_location_by_distance(re)

        return BatchGeocodeResponse(results=results, failed=failed)


    async def import_data_from_csv(
        self,
        user_lat: float,
        user_lon: float,
        file_path: str
    ):
        all_rows = []

        with open(file_path, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                sanitized_row = ",".join(row)   
                all_rows.append(sanitized_row)  

        results = await self.geocode_with_thread_pool(all_rows, user_lat, user_lon) 
        return results  
        