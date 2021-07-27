from django.shortcuts import render, HttpResponse, redirect, reverse, HttpResponseRedirect
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from .models import Book, DailyUserReadingGoal, Highlight, Review, UserBook, UserReadingGoal, Author, Genre, WishList
from django.shortcuts import get_object_or_404
import pandas as pd
import numpy as np
from django.templatetags.static import static
import os
from django.conf import settings
from django.utils.decorators import method_decorator
import json
from django.contrib.auth.decorators import login_required
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from PyDictionary import PyDictionary
import io
import os
import datetime
import random
from pdf2image import convert_from_path

# Create your views here.

STATIC_FILE_URI = r"C:\Users/User/Desktop/Projects/IBMINTERNSHIP/static/csv/books.csv"


class IndexView(View):
    template_name = "index.html"

    def get(self, request):
        context = {}
        top_books = Book.objects.all().order_by('rating').reverse()
        most_read = Book.objects.all().order_by('read_count').reverse()
        # book = top_books[0]
        # images = convert_from_path('./media/' + book.file.name, 500, poppler_path=r"C:\Program Files\poppler-0.68.0\bin")
        # os.mkdir('temp')
        # for i in range(len(images)):
        #     images[i].save('temp/page'+ str(i) +'.jpg', 'JPEG')
        context['top_books'] = top_books[:3]
        context['most_read'] = most_read[:3]
        if(request.user.is_authenticated):
            wishlist = WishList.objects.filter(user = request.user)
            context['wishlist'] = wishlist
            print(wishlist)
        authors = Author.objects.all().order_by('rating').reverse()
        context['authors'] = authors[:3]
        # start_date = datetime.date.today()
        # for single_date in (start_date - datetime.timedelta(n) for n in range(7, -1 , -1)):
        #     d = DailyUserReadingGoal(date = single_date, user = request.user, base = get_object_or_404(UserReadingGoal, user = request.user), completedminutes=float(random.randint(20, 60)))
        #     d.save()
        return render(request, self.template_name, context)
    
    def post(self, request):
        query = request.POST['TitleOfBook']
        return redirect('/search/' + query)


class AddBook(View):
    template_name = "addbook.html"

    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        if (user.is_superuser):
            return render(request, self.template_name)
        else:
            return render(request, 'notadmin.html')

    @method_decorator(login_required)
    def post(self, request):
        reqdata = request.POST
        genre=reqdata['genre']
        author=reqdata['author']
        bookgenre = Genre.objects.filter(name = genre.title())
        
        if(len(bookgenre) > 0):
            bookgenre = bookgenre[0]
        else:
            bookgenre = Genre(name = genre.title())
            bookgenre.save()
        
        bookauthor = Author.objects.filter(name = author.title())
        
        if(len(bookauthor) > 0):
            bookauthor = bookauthor[0]
            bookauthor.rating = ((bookauthor.rating * bookauthor.ratingscount) + (reqdata['rating'] * reqdata['ratingscount']))/(bookauthor.ratingscount + reqdata['ratingscount'])
            bookauthor.ratingscount += reqdata['ratingscount']
            bookauthor.save()
        else:
            bookauthor = Author(name = reqdata['author'].title(), rating = reqdata['rating'], ratingscount = reqdata['ratingscount'])
            bookauthor.save()
        book = Book(
            name=reqdata['name'],
            file=request.FILES['file'],
            link=reqdata['link'],
            genre = bookgenre,
            author = bookauthor,
            cover_image=request.FILES['cover_image'],
            language=reqdata['language'],
            numberofpages=reqdata['numberofpages'],
            publisheddate=reqdata['publisheddate'],
            description=reqdata['description'],
            publisher=reqdata['publisher'],
            rating=reqdata['rating'],
            internationalBookNumber=reqdata['internationalBookNumber'],
            ratingscount=reqdata['ratingscount'],
            reviewscount=reqdata['reviewscount'],
        )
        book.save()
        
        fp = open('./media/' + book.file.name, 'rb')
        book.numberofpages = len(list(PDFPage.get_pages(fp)))
        book.save()
        return redirect("add_book")


def booksByName(request):
    name = request.GET.get('name', None)
    df = pd.read_csv(STATIC_FILE_URI, error_bad_lines=False)
    df.rename(columns={'  num_pages': 'pages'}, inplace=True)
    df = df[df['title'].str.lower().str.find(name.lower()) != -1]
    response = json.loads(json.dumps(df.to_json(orient='records')))
    return HttpResponse(content=response)


def bookDetailsByName(request):
    name = request.GET.get('name', None)
    print(name)
    df = pd.read_csv(STATIC_FILE_URI, error_bad_lines=False)
    df.rename(columns={'  num_pages': 'pages'}, inplace=True)
    df = df[df["title"] == name].head(1)
    response = json.loads(json.dumps(df.to_json(orient='records')))
    return HttpResponse(content=response)


class BookDetailView(View):
    template_name = "bookdetails.html"

    @method_decorator(login_required)
    def get(self, request, **kwargs):
        book = get_object_or_404(Book, id=kwargs['pk'])
        wishlist = WishList.objects.filter(user = request.user, book = book)
        b = {'object': book}
        response = b
        review = Review.objects.filter(book=book, user=request.user)
        c = {'review': review}
        reviews = Review.objects.filter(book=book)
        d = {'reviews':reviews}
        response = {**b, **c, **d}
        if(len(wishlist) > 0):
            e = {'wishlist': wishlist}
            response = {**b, **c, **d, **e}

        return render(request, self.template_name, response)

    def post(self, request, **kwargs):
        book = get_object_or_404(Book, id=kwargs['pk'])
        review = Review(
            user=request.user,
            book=book,
            rating=float(request.POST['rating']),
            review=request.POST['review'],
        )
        book.reviewscount += 1
        book.ratingscount += 1
        book.rating = ((book.ratingscount * book.rating) + float(request.POST['rating']))/(book.ratingscount+1)
        book.save()
        next = request.POST.get('next', '/')
        review.save()
        return HttpResponseRedirect(next)


class ReadBookView(View):
    template_name = "readbook.html"

    @method_decorator(login_required)
    def get(self, request, **kwargs):
        book = get_object_or_404(Book, id=kwargs['pk'])
        userbook = UserBook.objects.filter(book=book, user=request.user)
        context = {}
        context['book'] = book
        fp = open('./media/' + book.file.name, 'rb')
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = []
        page_no = 0
        for pageNumber, page in enumerate(PDFPage.get_pages(fp)):
            if pageNumber == page_no:
                interpreter.process_page(page)
                data = retstr.getvalue()
                pages.append(data)
                data = ''
                retstr.truncate(0)
                retstr.seek(0)
                page_no += 1
        if (len(userbook) == 0):
            book.read_count += 1
            book.save()
            userbook = UserBook(book=book, user=request.user)
            userbook.save()
            context['userbook'] = userbook
            context['page'] = pages[0]

        else:
            book.read_count += 1
            book.save()
            userbook[0].save()
            context['userbook'] = userbook[0]
            context['page'] = pages[userbook[0].last_open_page - 1]
            context['page'] = context['page'].replace("\x0c", "")
            highlight = Highlight.objects.filter(userbook=userbook[0], page=userbook[0].last_open_page)
            
            for i in highlight:
                context['page'] = context['page'].replace(i.text , "<span class='highlight'>" + i.text + "</span>")
        return render(request, self.template_name, context)

@login_required()    
def highlight(request, **kwargs):
    book = get_object_or_404(Book, id=kwargs['pk'])
    userbook = get_object_or_404(UserBook, book=book, user=request.user)
    highlight = Highlight(userbook = userbook, page = userbook.last_open_page, text = kwargs['text'])
    highlight.save()
    return redirect('/read/' + str(kwargs['pk']))


@login_required()
def next_page(request, **kwargs):
    book = get_object_or_404(Book, id=kwargs['pk'])
    userbook = get_object_or_404(UserBook, book=book, user=request.user)
    userbook.last_open_page += 1
    userbook.save()
    return redirect('/read/' + str(kwargs['pk']))


@login_required()
def previous_page(request, **kwargs):
    book = get_object_or_404(Book, id=kwargs['pk'])
    userbook = get_object_or_404(UserBook, book=book, user=request.user)
    userbook.last_open_page -= 1
    userbook.save()
    return redirect('/read/' + str(kwargs['pk']))


class Dashboard(View):
    template_name = "dashboard.html"
    
    @method_decorator(login_required)
    def get(self, request):
        userbook = UserBook.objects.filter(user = request.user)
        readinggoal = UserReadingGoal.objects.filter(user = request.user)
        context = {}
        wishlist = WishList.objects.filter(user = request.user)
        context['wishlist'] = wishlist
        if(len(readinggoal) > 0):
            context['readinggoal'] = readinggoal[0]
            todaysgoal = get_object_or_404(DailyUserReadingGoal, user=request.user, date = datetime.datetime.today())
            context['todaysgoal'] = todaysgoal
            percent = (todaysgoal.completedminutes / readinggoal[0].minutes) * 100
            if(percent > 100):
                percent = 100.0
            context['percent'] = round(percent,1)
            start_date = datetime.date.today()
            delta = datetime.timedelta(days=1)
            i=0
            pastgoals = []
            dates = []
            for x in range(7):
                pastgoal = DailyUserReadingGoal.objects.filter(user = request.user, date = start_date)
                if(len(pastgoal) > 0):
                    pastgoals.append(round(pastgoal[0].completedminutes,1)) 
                else:
                    pastgoals.append(0)
                dates.append(start_date)
                start_date -= delta
            pastgoals.reverse()
            percentpastgoals = []
            if(max(pastgoals) > 0):
                for i in range(7):
                    percentpastgoals.append(round((pastgoals[i]/max(pastgoals))*100,1))
            else:
                percentpastgoals = pastgoals
            context['pastgoals'] = percentpastgoals
            context['weekavg'] = sum(pastgoals) / len(pastgoals)
            context['dates'] = dates
    
        context['userbooks'] = userbook
        percentbook=[]
        for i in userbook:
            percentbook.append(round((i.last_open_page / i.book.numberofpages) * 100, 2))
        context['percentbook'] = percentbook
        return render(request, self.template_name, context) 
    
    @method_decorator(login_required)
    def post(self, request):
        readinggoal = UserReadingGoal(user = request.user, minutes = request.POST['minutes'])
        readinggoal.save()
        userreadinggoal = DailyUserReadingGoal(user = request.user, base = readinggoal, completedminutes=0.0, date = datetime.datetime.today())
        userreadinggoal.save()
        return redirect('/dashboard')
    
@login_required()
def meaning(request, **kwargs):
    dict = PyDictionary()
    meaning = dict.meaning(request.GET['text'].strip())
    return HttpResponse(json.dumps(meaning))

@login_required()
def updateGoal(request, **kwargs):
    minutes = int(request.GET['timeSpent'])/60000
    todaysgoal = get_object_or_404(DailyUserReadingGoal, user=request.user, date = datetime.datetime.today())
    todaysgoal.completedminutes += minutes
    todaysgoal.save()
    return HttpResponse()


class AuthorsView(View):
    template_name = "authors.html"
    context = {}
    
    def get(self, request):
        authors = Author.objects.all()
        self.context['authors'] = authors
        return render(request, self.template_name, self.context)
    
class GenreView(View):
    template_name = "genres.html"
    context = {}
    
    def get(self, request):
        genres = Genre.objects.all()
        books = Book.objects.all()
        self.context['genres'] = genres
        self.context['books'] = books
        return render(request, self.template_name, self.context)

class AuthorDetailsView(View):
    template_name = "authordetail.html"
    context = {}
    
    def get(self, request, **kwargs):
        author = get_object_or_404(Author,id = kwargs['pk'])
        self.context['author'] = author
        books = Book.objects.filter(author=author)
        print(author)
        self.context['books'] = books
        return render(request, self.template_name, self.context)
    
class BooksView(View):
    template_name = "books.html"
    context = {}
    
    def get(self, request):
        books = Book.objects.all()
        self.context['books'] = books
        if(request.user.is_authenticated):
            wishlist = WishList.objects.filter(user = request.user)
            self.context['wishlist'] = wishlist
        return render(request, self.template_name, self.context)
    
def Search(request, query):
    if(request.method == "POST"):
        return redirect('/search/' + request.POST['TitleOfBook'])
    books = Book.objects.filter(name__contains = query.lower())
    context = {}
    context['books'] = books
    authors = Author.objects.filter(name__contains = query.lower())
    context['authors'] = authors
    genres = Genre.objects.filter(name__contains = query.lower())
    context['genres'] = genres
    if(len(genres) > 0):
        genrebooks = Book.objects.filter(genre = genres[0])
        context['genrebooks'] = genrebooks
    return render(request, 'search.html', context)

@login_required()
def addToWishlist(request, **kwargs):
    book = get_object_or_404(Book, id = kwargs['pk'])
    user = request.user
    wishlist = WishList(user = user, book = book)
    wishlist.save()
    return HttpResponse({'message': 'successfully added'})

@login_required()
def removeFromWishlist(request, **kwargs):
    book = get_object_or_404(Book, id = kwargs['pk'])
    user = request.user
    wishlist = get_object_or_404(WishList,user = user, book = book)
    wishlist.delete()
    return HttpResponse({'message': 'successfully deleted'})

@login_required()
def addToWishlistBook(request, **kwargs):
    book = get_object_or_404(Book, id = kwargs['pk'])
    user = request.user
    wishlist = WishList(user = user, book = book)
    wishlist.save()
    return redirect('/book/' + str(kwargs['pk']))

@login_required()
def removeFromWishlistBook(request, **kwargs):
    book = get_object_or_404(Book, id = kwargs['pk'])
    user = request.user
    wishlist = get_object_or_404(WishList,user = user, book = book)
    wishlist.delete()
    return redirect('/book/' + str(kwargs['pk']))
    