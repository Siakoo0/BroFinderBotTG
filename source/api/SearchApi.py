from source.api.ApiRequest import ApiRequest

class SearchApiHelper(ApiRequest):
    @property
    def resource(self):
        return "search"