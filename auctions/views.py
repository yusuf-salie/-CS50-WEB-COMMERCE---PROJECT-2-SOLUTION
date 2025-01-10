from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Listing, User, Category, Listing, Comment, Bid

# Listing details view
def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments
    })
    
def addComment(request,id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST['newComment']

    newComment = Comment(
        author=currentUser,
        listing=listingData,
        message=message
    )
    newComment.save()
    
    return HttpResponseRedirect(reverse("listing", args=(id, )))

# Watchlist view - show the user's watchlist
def watchlist_view(request):
    current_user = request.user
    watchlist_listings = request.user.watchlist_items.all()
    # Get the listings in the user's watchlist
    watchlist_listings = Listing.objects.filter(watchlist=current_user)
    return render(request, 'auctions/watchlist.html', {'watchlist_listings': watchlist_listings})

# Add a listing to the user's watchlist
def addWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def displayWatchList(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "action/watchlist.html", {
        "listings": listings
    })


# Remove a listing from the user's watchlist
def removeWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id,)))

# Display active listings on the homepage
def index(request):
    activeListing = Listing.objects.filter(isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListing,
        "categories": allCategories
    })

# Display listings filtered by category
def displayCategory(request):
    if request.method == "POST":
        categoryFromForm = request.POST['category']
        category = Category.objects.get(categoryName=categoryFromForm)
        activeListing = Listing.objects.filter(isActive=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/display_category.html", {
            "listings": activeListing,
            "categories": allCategories
        })

# Create a new listing
def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
        # Get data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        price = request.POST["price"]
        category = request.POST["category"]
        currentUser = request.user
        #Who is the user
        currentUser = request.user
        
        #Get all content about the particular category
        categoryData = Category.objects.get(categoryName=category)
        #Create a bid object
        bid = Bid(bid=int(price), user=currentUser)
        bid.save()
        
        # Check if all required fields are provided
        if not all([title, description, imageurl, price, category]):
            return render(request, "auctions/create.html", {
                "error": "All fields are required!",
                "categories": Category.objects.all(),
            })

        # Ensure price is a valid number
        try:
            price = float(price)
        except ValueError:
            return render(request, "auctions/create.html", {
                "error": "Please enter a valid price.",
                "categories": Category.objects.all(),
            })
        
        # Get the category object
        categoryData = Category.objects.get(categoryName=category)
        
        # Create and save the listing
        newListing = Listing(
            title=title,
            description=description,
            imageUrl=imageurl,
            price=bid,
            category=categoryData,
            owner=currentUser
        )
        newListing.save()

        # Redirect to the index page after successful creation
        return HttpResponseRedirect(reverse('index'))

# Login view
def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication is successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

# Logout view
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# Registration view
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create a new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    # Your logic for creating a listing
    return render(request, 'auctions/create_listing.html')
