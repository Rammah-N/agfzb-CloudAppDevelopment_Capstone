import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        
    except:
        # If any error occurs
        print("Network exception occurred")
    # status_code = response.status_code
    # print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            
            results.append(dealer_obj)
    print(results)
    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id):
    dealer_reviews = []
    # Call get_request with a URL parameter
    json_result = get_request("https://ramahnore-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews", id=dealer_id)
    if json_result:
        reviews = json_result
        print(reviews)
        for review in reviews:
            dealer_review = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                review=review["review"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment="",
                id=review["id"],
            )
            dealer_review.sentiment = analyze_review_sentiments(dealer_review.review)
            dealer_reviews.append(dealer_review)
       
    return dealer_reviews

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

def analyze_review_sentiments(dealerreview):
    body = {"text": dealerreview, "features": {"sentiment": {"document": True}}}
    try:
        response = requests.post(
            url ="https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/7915b459-2bce-423a-8092-90cb059852b5/v1/analyze?version=2022-04-07",
            headers={"Content-Type": "application/json"},
            json=body,
            auth=HTTPBasicAuth("apikey", "nMk5TABLvboHSIRh3PHqCm06bLbmw0zbIX1wUvyrPG7c"),
        )
        if response.status_code == 200:
            sentiment = response.json()["sentiment"]["document"]["label"]
            return sentiment
        else:
            return f"Error: Status code {response.status_code}, {response.text}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

