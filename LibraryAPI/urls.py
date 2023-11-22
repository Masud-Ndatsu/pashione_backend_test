from django.urls import path
from . import views

urlpatterns = [
    path("books/listing", views.get_book_listing),
    path("books/add", views.create_book),
    path("books/edit", views.update_book),
    path("books/delete", views.delete_book),
    path('books/<int:book_id>/', views.get_book_by_id, name='get_book_by_id')
]