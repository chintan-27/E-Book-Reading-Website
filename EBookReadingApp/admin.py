from django.contrib import admin
from .models import Book, UserBook, Highlight, Review, UserReadingGoal, DailyUserReadingGoal, Author, Genre, WishList

# Register your models here.
admin.site.register(Book)
admin.site.register(UserBook)
admin.site.register(Highlight)
admin.site.register(Review)
admin.site.register(UserReadingGoal)
admin.site.register(DailyUserReadingGoal)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(WishList)