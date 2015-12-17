from django.contrib import admin

from .models import *


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 3


class BookInline(admin.TabularInline):
    model = Book
    extra = 6


class AuthorAdmin(admin.ModelAdmin):
    inlines = [BookInline]
    list_display = ['name']
    search_fields = ['name']

class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'isbn', 'title', 'authors', 'genres', 'price', 'discount', 'stock')
    search_fields = ['id', 'isbn', 'title', 'price']

class OrderHistoryAdmin(admin.ModelAdmin):
    inlines = [OrderLineInline]
    list_display = ('id', 'fullname', 'order_date', 'status', 'total', 'shipping_fee', 'total_include_shipping')
    search_fields = ['id', 'fullname', 'order_date']
    readonly_fields = ('fullname', 'order_date', 'total')
    list_filter = ['status']


class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'bill_no', 'created_date', 'total_amount', 'note')
    search_fields = ['id', 'bill_no', 'created_date']


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'fullname', 'email', 'phone')
    search_fields = ['id', 'username', 'fullname', 'email', 'phone']
    readonly_fields = ('username', 'fullname', 'email', 'phone', 'city', 'district', 'ward', 'postal_code', 'street_number')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['id', 'name']


class PublisherAdmin(admin.ModelAdmin):
    inlines = [BookInline]
    list_display = ['id', 'name']
    search_fields = ['name']


# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(Bill, BillAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(OrderHistory, OrderHistoryAdmin)
admin.site.register(Publisher, PublisherAdmin)