from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Listing, User, Category, Comment, Bid

# Listing details view
def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner
    })    

def closeAuction(request, id):
    # Correctly access the Listing model's manager
    listingData = Listing.objects.get(pk=id)  # Correcting this line
    listingData.isActive = False
    listingData.save()

    # Check if the current user is the owner of the listing
    isOwner = request.user.username == listingData.owner.username

    # Check if the current user has the listing in their watchlist
    isListingInWatchlist = request.user in listingData.watchlist.all()

    # Fetch all comments related to the listing
    allComments = Comment.objects.filter(listing=listingData)

    # Render the response
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "update": True,
        "message": "Congratulations! Your auction is closed."
    })


from django.shortcuts import render, get_object_or_404
from .models import Listing, Bid, Comment

from django.shortcuts import render, get_object_or_404
from .models import Listing, Bid, Comment

def addBid(request, id):
    listingData = get_object_or_404(Listing, pk=id)
    isOwner = request.user.username == listingData.owner.username
    newBid = int(request.POST['newBid']) if request.method == "POST" else None  # Get the new bid value as an integer
    isListingInWatchlist = request.user in listingData.watchlist.all()

    if request.method == "POST":
        # Make sure you are comparing the bid value correctly
        if newBid > listingData.price.bid:  # Compare with the current bid value
            updateBid = Bid(user=request.user, bid=newBid)  # Create a new bid with the user and the new bid value
            updateBid.save()
            listingData.price = updateBid  # Update the listing's price to the new bid
            listingData.save()

            # Pass context to the template
            return render(request, "auctions/listing.html", {
                "listing": listingData,
                "message": "Bid was updated successfully",
                "update": True,
                "isListingInWatchlist": isListingInWatchlist,
                "allComments": Comment.objects.filter(listing=listingData),
                "isOwner": isOwner,
            })
        else:
            # If the bid is not higher, show the error message
            return render(request, "auctions/listing.html", {
                "listing": listingData,
                "message": "Bid update unsuccessful. New bid must be higher than the current bid.",
                "update": False,
                "isListingInWatchlist": isListingInWatchlist,
                "allComments": Comment.objects.filter(listing=listingData),
                "isOwner": isOwner,
            })
    else:
        # Pass context to the template
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": Comment.objects.filter(listing=listingData),
            "isOwner": isOwner,
        })

def closeBid(request, id):
    listingData = get_object_or_404(Listing, pk=id)
    if request.user.username == listingData.owner.username:
        listingData.is_open = False
        listingData.save()
    return redirect('listing', id=id)


def addComment(request, id):
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
    return render(request, "auctions/watchlist.html", {
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
            "categories": allCategories,
            "selected_category": categoryFromForm
        })
    else:
        allCategories = Category.objects.all()
        return render(request, "auctions/display_category.html", {
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
        
        # Get all content about the particular category
        categoryData = Category.objects.get(categoryName=category)
        
        # Create a bid object
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
