from aiohttp import ClientSession

from abc import ABCMeta, abstractproperty

class ApiRequest(metaclass=ABCMeta):
    @property
    def base_url(self):
        return "http://localhost:8080/api/"
    
    @abstractproperty
    def resource(self):
        pass
    
    @property
    def url(self):
        return self.base_url + self.resource
    
    async def get_one(self, id):
        return await self.request("GET", f"{self.url}/{id}")
    
    async def get(self, params):
        return await self.request("GET", self.url, params)
    
    async def create(self, params):
        return await self.request("POST", self.url, params)

    async def put(self, params):
        async with ClientSession() as session:
            async with session.put(self.url, data=params) as s:
                return await s.json()
            
    async def request(self, method, url, params=None):
        request_ = {
            "method" : method,
            "url" : url,
        }
        
        if method == "GET":
             request_["params"] = params
        else:
            request_["json"] = params
            
        async with ClientSession() as session:
            async with session.request(**request_) as s:
                return await s.json()
