from django.urls import path
from .views import AuthorDetailsView, BooksView, IndexView, AddBook, BookDetailView, ReadBookView, Dashboard, GenreView, AuthorsView
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from scheduler import scheduler


urlpatterns = [
    path('', IndexView.as_view(), name="home"),
    path('addbook', AddBook.as_view(), name="add_book"),
    path('getbooks', views.booksByName,name="books_details"),
    path('getbook', views.bookDetailsByName,name="book_details"),
    path(r'book/<int:pk>', BookDetailView.as_view(), name='book_detail_view'),
    path(r'author/<int:pk>', AuthorDetailsView.as_view(), name='author_detail_view'),
    path(r'read/<int:pk>', ReadBookView.as_view(), name='read_book_view'),
    path(r'next/<int:pk>', views.next_page, name='next_page'),
    path(r'previous/<int:pk>', views.previous_page, name='previous_page'),
    path(r'highlight/<int:pk>/<str:text>', views.highlight, name='highlight'),
    path('genres', GenreView.as_view(), name='genres'),
    path('books', BooksView.as_view(), name='books'),
    path('authors', AuthorsView.as_view(), name='authors'),
    path('meaning', views.meaning, name='meaning'),
    path('dashboard', Dashboard.as_view(), name='dashboard'),
    path('updategoal', views.updateGoal, name="update_goal"),
    path('search/<str:query>', views.Search, name="Search"),
]
urlpatterns+= staticfiles_urlpatterns()
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

scheduler.start()