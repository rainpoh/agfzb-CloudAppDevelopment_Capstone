import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth
from .models import CarDealer, DealerReview

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
# def get_request(url, **kwargs):
#     print(kwargs)
#     print("GET from {} ".format(url))
#     response = {}
#     try:
#         if 'api_key' in kwargs.keys():
#             api_key = kwargs['api_key']
#             # Basic authentication GET
#             print("Basic authentication GET")
#             response = requests.get(url, params=params, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', api_key))
#         else:
#             # Call get method of requests library with URL and parameters
#             print("NO authentication GET")
#             response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
#     except:
#         # If any error occurs
#         print("Network exception occurred")
#     status_code = response.status_code
#     print("With status {} ".format(status_code))
#     json_data = json.loads(response.text)
#     return json_data


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    return requests.post(url, params=kwargs, json=payload)

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"],
            )
            results.append(dealer_obj)
    return results

def get_dealer_by_id(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"],
            )
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if len(json_result['docs']) != 0:
        if json_result:
            # Get the row list in JSON as dealers
            reviews = json_result['docs']
            # For each dealer object
            for review_doc in reviews:
                # Create a CarDealer object with values in `doc` object
                review_obj = DealerReview(
                    dealership=review_doc.get('dealership', ''),
                    name=review_doc.get("name", ''),
                    purchase=review_doc.get('purchase', ''),
                    review=review_doc.get('review', ''),
                    purchase_date=review_doc.get('purchase_date', ''),
                    car_make=review_doc.get('car_make', ''),
                    car_model= review_doc.get('car_model', ''),
                    car_year=review_doc.get('car_year', ''),
                    sentiment=analyze_review_sentiments(review_doc.get('review', '')),
                    id=review_doc.get('id', ''),
                )
                results.append(review_obj)
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    URL = 'https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/db169282-5450-4778-a190-c4282eb8f986/v1/analyze'
    API_KEY = 'i_wqYb8rMAPZNZijkV2jAXdmybYivGndbP76f7ShlySw'
    params = json.dumps({"text": text, "version": "2021-08-01", "features": {"sentiment": {}}})
    response = requests.post(
        URL, data=params, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', API_KEY)
    )
    try:
        return response.json()['sentiment']['document']['label']
    except KeyError:
        return 'unknown'