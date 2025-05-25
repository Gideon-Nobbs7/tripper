import asyncio
import http.client
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from os import getenv
from typing import List, Optional

import aiohttp
import httpx
from dotenv import load_dotenv

from src.exceptions import GeocodeError

load_dotenv()


class GeocodeClass:
    def __init__(self):
        self.auth = getenv("AUTH_KEY")

    def get_coordinates_for_address(self, location):
        conn = http.client.HTTPConnection("geocode.xyz")

        payload = {
            "auth": self.auth,
            "locate": f"{location}, Kumasi, Ghana",
            # "region": "Ghana",
            "json": 1   
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
            lattitude = float(data["latt"])

            if longitude == 0.0 and lattitude == 0.0:
                raise GeocodeError(
                    "No valid coordinates returned for the location. Try adding a city or country separated by comma"
                )
            
            return {
                "location": location,
                "longitude": longitude,
                "latitude": lattitude,
                "status": "success"
            }
        except Exception as e:
            raise GeocodeError(str(e))
        # print(response.decode("utf-8"))    



    async def get_coordinates_async_aiohttp(
            self,
            location: str,
            session: aiohttp.ClientSession
    ):
        url = "geocode.xyz"
        params = {
            "auth": self.auth,
            "locate": f"{location}, Kumasi, Ghana",
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
        locations: List[str]
    ):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = [
                loop.run_in_executor(executor, self.get_coordinates_for_address, location)
                for location in locations
            ]
            return await asyncio.gather(*tasks)