from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('update/', views.update, name='update'),
    path('delete/', views.delete, name='delete'),
    path('books/', views.BooksView.as_view(), name='show-books'),
    path('authors/', views.AuthorView.as_view(), name='show-authors'),
    re_path(r'^book/(?P<pk>\d+)/$', views.BookDetailView.as_view(), name='book-detail'),
    re_path(r'^author/(?P<pk>\d+)/$', views.AuthorDetailView.as_view(), name='author-detail'),
    path('mybook/', views.mybook, name='mybook'),
    path('manage-borrowed-books/', views.manage_borrowed_books, name='manage-borrowed-books'),
    path('<id>/suspend-due-back/', views.MarkFormView.as_view(), name='mark'),
    path('create-author/', views.CreateAuthorModelFormView.as_view(), name='create-author'),
    path('edit-author/<pk>/', views.UpdateAuthorModelFormView.as_view(), name='edit-author'),
    path('delete-author/<pk>/', views.DeleteAuthorView.as_view(), name='delete-author')
]