from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('category/', views.displayCategory, name='displayCategory'),
    path("watchlist/", views.watchlist_view, name="watchlist"),
    path("listing/<int:id>/", views.listing, name="listing"),
    path('listing/<int:id>/add/', views.addWatchlist, name='addWatchlist'),
    path('listing/<int:id>/remove/', views.removeWatchlist, name='removeWatchlist'),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.createListing, name="createListing"),
    path('create/', views.create_listing, name='create'),
    path("addComment/<int:id>", views.addComment, name="addComment"),
    path("addBid/<int:id>", views.addBid, name="addBid"),
    path("closeAuction/<int:id>", views.closeAuction, name="closeAuction"),
    path('closeBid/<int:id>/', views.closeBid, name='closeBid'),    
]