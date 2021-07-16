from os import read
from django.db import models
from django.conf import settings
import datetime

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=200)
    rating = models.FloatField(default=0.0)
    image = models.ImageField(null=True)
    ratingscount = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
class Genre(models.Model):
    name = models.CharField(max_length=200)
    readcount = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre,on_delete=models.CASCADE)
    file = models.FileField(upload_to='books/', blank=True, null=True)
    description = models.TextField()
    link = models.CharField(max_length=500, null=True, blank=True)
    cover_image = models.ImageField(upload_to='img/')
    read_count = models.IntegerField(default=0)
    numberofpages = models.IntegerField()
    language = models.CharField(max_length=100)
    internationalBookNumber = models.CharField(max_length=200, default="")
    rating = models.FloatField(default=0)
    publisher = models.CharField(max_length=300)
    publisheddate = models.CharField(max_length=20)
    ratingscount = models.IntegerField(default=0)
    reviewscount = models.IntegerField(default=0)
    

    def __str__(self):
        return self.name

class UserBook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    last_open_date_time = models.DateTimeField(auto_now=True)
    last_open_page = models.IntegerField(default=1)

    def __str__(self):
        return str(self.user.id) + " " + str(self.book.id)

class Highlight(models.Model):
    userbook = models.ForeignKey(UserBook, on_delete=models.CASCADE)
    page = models.IntegerField()
    text = models.TextField()
    
    def __str__(self):
        return str(self.userbook.id) + str(self.page)
    
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.FloatField()
    review = models.TextField()
    
    def __str__(self):
        return str(self.user.id) + " " + str(self.book.id)
    
class UserReadingGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    minutes = models.IntegerField()
    
    def __str__(self):
        return self.user.username
    
class DailyUserReadingGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    base = models.ForeignKey(UserReadingGoal,on_delete=models.CASCADE)
    completedminutes = models.FloatField()
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username + " " + str(self.date)
    
# class PageImage(models.Model):
#     book = models.ForeignKey(Book, on_delete=models.CASCADE)
#     page_number = models.IntegerField()
#     image = models.ImageField(upload_to="img/bookimages/")
    
#     def __str__(self):
#         return self.book.name + " " + self.page_number
    