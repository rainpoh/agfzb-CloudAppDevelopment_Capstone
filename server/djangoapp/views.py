from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_by_id, get_dealer_reviews_from_cf, post_request

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/99b2deb1-937e-4aa4-a2b8-ed589839f2f0/dealership/get-dealership"
         # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context = {
            "dealerships": dealerships,
        }
        return render(request, 'djangoapp/index.html', context)

# def get_dealerships(request):
#     if request.method == "GET":
#         url = "your-cloud-function-domain/dealerships/dealer-get"
#         # Get dealers from the URL
#         dealerships = get_dealers_from_cf(url)
#         # Concat all dealer's short name
#         dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
#         # Return a list of dealer short name
#         return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url_dealership = f"https://us-south.functions.appdomain.cloud/api/v1/web/99b2deb1-937e-4aa4-a2b8-ed589839f2f0/dealership/get-dealership?dealerId={dealer_id}"
        url_review = f"https://us-south.functions.appdomain.cloud/api/v1/web/99b2deb1-937e-4aa4-a2b8-ed589839f2f0/dealership/get-review?dealerId={dealer_id}"
        # Get dealers from the URL
        context = {
            "dealer": get_dealer_by_id(url_dealership, dealer_id)[0],
            "reviews": get_dealer_reviews_from_cf(url_review, dealer_id),
        }
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    if request.method == "GET":
        url = f"https://us-south.functions.appdomain.cloud/api/v1/web/99b2deb1-937e-4aa4-a2b8-ed589839f2f0/dealership/get-dealership?dealerId={dealer_id}"
        # Get dealers from the URL
        context = {
            "cars": CarModel.objects.all(),
            "dealer": get_dealer_by_id(url, dealer_id)[0],
        }
        print(context)
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
        form = request.POST
        review = {
            "name": f"{request.user.first_name} {request.user.last_name}",
            "dealership": dealer_id,
            "review": form["content"],
            "purchase": form.get("purchasecheck"),
            }
        if form.get("purchasecheck"):
            review["purchasedate"] = datetime.strptime(form.get("purchasedate"), "%m/%d/%Y").isoformat()
            car = CarModel.objects.get(pk=form["car"])
            review["car_make"] = car.car_make.name
            review["car_model"] = car.name
            review["car_year"]= car.year.strftime("%Y")
        json_payload = {"review": review}
        URL = 'https://us-south.functions.appdomain.cloud/api/v1/web/99b2deb1-937e-4aa4-a2b8-ed589839f2f0/dealership/post-review'
        post_request(URL, json_payload, dealerId=dealer_id)
    return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
