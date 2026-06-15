import asyncio
import aiohttp

class UnivacKvmClient:
    """ Polling engine for the Sperry KVM GUI to ingest the centralized threat matrix """
    def __init__(self, aegis_url: str):
        self.aegis_url = aegis_url
        self.session = None

    async def initialize(self):
        """ Instantiates the asynchronous HTTP session """
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2.0))

    async def shutdown(self):
        """ Gracefully closes the outbound sockets """
        if not self.session:
            return
        await self.session.close()

    async def fetch_threat_matrix(self) -> list:
        """ Asynchronously pulls the current active alarm states from the Aegis core """
        if not self.session:
            return []

        headers = {"X-Aegis-Client": "Univac-Sperry-KVM-Console"}
        
        try:
            async with self.session.get(self.aegis_url + "/status", headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception:
            return []
