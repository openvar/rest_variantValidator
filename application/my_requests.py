# import the requests module
import requests


# Create the class
class MyRequests:

    def __init__(self):
        self.base_url = None
        self.url = None

    # method that makes the call to the API using the get method:
    def request_data(self, prms = None):
        return requests.get(self.url, params = prms)

    # method that assembles the url to request data from the hello endpoint:
    def hello(self):
        self.url = f"{self.base_url}hello"
        return self.request_data()

    # method to get data from the name endpoint:
    def name_get(self, name):
        self.url = f"{self.base_url}name/{name}"
        return self.request_data()
    
    # method to get data from the VariantValidator endpoint: ## Have been quite confused about what the last two bits of exercise 2 are asking for - is it make changes to app v3 to add requesting diff. content types and then to here?
    def VV_get(self, gbuild, vdesc, seltrans, content_type = None):

        # If want to request as xml:
        if content_type == 'xml':
            self.url = f"{self.base_url}VariantValidator/{gbuild}/{vdesc}/{seltrans}?content-type=text/xml"

        # If want to request as json:
        elif content_type == 'json':
            self.url = f"{self.base_url}VariantValidator/{gbuild}/{vdesc}/{seltrans}?content-type=application/json"
        
        # Else use default url:
        else:
            self.url = f"{self.base_url}VariantValidator/{gbuild}/{vdesc}/{seltrans}"
        
        return self.requestdata
    


if __name__ == "__main__":
    mrq = MyRequests()
    
    # Set the base url
    mrq.base_url = "http://127.0.0.1:5000/"
    
    ### hello endpoint:
    # request the data
    response_hello = mrq.hello()
    
    # print the 3 response sections
    print(response_hello.status_code)
    print(response_hello.headers)
    print(response_hello.text)
    print(response_hello.json())

    ### name endpoint:
    name = 'Tom'
    response_nm = mrq.name_get(name)
    print(response_nm.status_code)
    print(response_nm.headers)
    print(response_nm.text)
    print(response_nm.json())

    ## VariantValidator endpoint - left these blank for now:
    gbuild = '_____'
    vdesc = '_____'
    seltrans = '_____'
    response_VV = mrq.VV_get(gbuild, vdesc, seltrans)
    
    print(response_VV.status_code)
    print(response_VV.json())