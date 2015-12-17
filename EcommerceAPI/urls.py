__author__ = 'Duy'

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^genre/$', views.get_genres, name='get-genres'), # done
    url(r'^book/$', views.get_books, name='get-books'), # done
    url(r'^book/get/$', views.get_book_by_id, name='get-book-by-id'), # done
    url(r'^book/genre/$', views.get_books_by_genre, name='get-books-by-genre'), # done
    url(r'^book/new/$', views.get_new_books, name='get-new-books'), #done
    url(r'^book/search', views.search_book, name='search-book'), # done
    url(r'^book/recommendation/$', views.get_books_by_recommendation, name='get-books-by-recommendation'),
    url(r'^book/image/$', views.get_image, name='get-image'),
    url(r'^customer/login/$', views.log_in, name='log-in'), # done
    url(r'^customer/register/$', views.register, name='register'), # done
    url(r'^customer/profile/$', views.handle_profile, name='handle-profile'), # done
    url(r'^customer/oauth/request', views.request_oauth, name='request-oauth-url'),
    url(r'^order/$', views.handle_order, name='handle-order'), # done
    url(r'^order/customer/', views.get_orders_by_customer, name='get-orders-by-customer'), #done
]