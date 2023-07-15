from source.api.ApiRequest import ApiRequest

class ProductApiHelper(ApiRequest):
    @property
    def resource(self):
        return "product"
    
    async def search(self, text, filter, page=0, size=5):
        return await self.get({
            "text" : text,
            "filter" : filter,
            "page" : page,
            "size" : size
        })