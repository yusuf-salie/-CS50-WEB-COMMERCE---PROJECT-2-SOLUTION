from django.contrib import admin
from .models import User, Category, Listing, Comment

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Comment)