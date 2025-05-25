import asyncio
from os import getenv

import aiohttp
from dotenv import load_dotenv

load_dotenv()


class GeocodeError(Exception):
    pass


            