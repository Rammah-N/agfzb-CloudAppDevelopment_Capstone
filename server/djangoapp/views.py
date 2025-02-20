from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import DealerReview, CarModel
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import requests

from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html')
# ...


# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        login(request, user)
        return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/', context)
# ...

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)

    return render(request, 'djangoapp/index.html')
# ...

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp")
        else:
            return render(request, 'djangoapp/registration.html', context)
# ...

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://ramahnore-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
       
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    print('dealer id here')
    print(dealer_id)
    if request.method == "GET":
        url = "https://ramahnore-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        return render(
            request,
            "djangoapp/dealer_details.html",
            {"reviews": reviews, "dealer_id": dealer_id},
        )


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

def add_review(request, dealer_id):
    print('dealer_id here')
    print(dealer_id)
    context = {"dealer_id": dealer_id}

    if request.method == "GET":
        context["cars"] = CarModel.objects.all()
        print('context here')
        print(context['cars'])
        return render(request, "djangoapp/add_review.html", context)

    elif request.method == "POST":
        input_data = request.POST
        review = {
            "dealership": int(dealer_id),
            "review": input_data.get("content", ""),
            "purchase": input_data.get("purchasecheck", False) == 'on',
            "purchase_date": input_data.get("purchasedate", ""),
        }

        car_id = input_data.get("car")
        car = CarModel.objects.filter(pk=car_id).first()
        print('car here')
        print(car)
        required_fields = ['id', 'name', 'dealership', 'review', 'purchase', 'purchase_date', 'car_make', 'car_model', 'car_year']
        if car:
            review.update({
                "car_make": car.car_make.name,
                "car_model": car.name,
                "car_year": car.year.strftime("%Y"),
                "name": car.name,
                "id": 10
            })
        else:
            review.update({
                "car_make": "None",
                "car_model": "None",
                "car_year": "None",
            })
        response = requests.post(
            "https://ramahnore-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review", headers={"Content-Type": "application/json"}, json=review
        )
        print('post response here')
        print(response)
        if response.status_code == 201:
            
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            print(response.content)

    else:
        pass

    return render(request, "djangoapp/add_review.html", context)

