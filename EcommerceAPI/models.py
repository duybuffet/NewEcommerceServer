from EcommerceAPI.constants import ORDER_STATUS_WAITING, ORDER_STATUS_CONFIRMED, ORDER_STATUS_COMPLETED, \
    ORDER_STATUS_CANCEL
import constants
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
# from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.encoding import smart_unicode
import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

env = "BookEcommerce.settings"

# setup_environ(settings)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", env)

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class Author(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_author'

    def __str__(self):
        return smart_unicode(self.name)

    def __unicode__(self):
        return smart_unicode(self.name)

class Bill(models.Model):
    bill_no = models.CharField(max_length=45, blank=False, null=False, unique=True)
    note = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(blank=False, null=False)
    total_amount = models.FloatField()
    staff = models.ForeignKey(AUTH_USER_MODEL)
    order = models.ForeignKey('OrderHistory')

    class Meta:
        managed = False
        db_table = 'tbl_bill'

    def __str__(self):
        if self.bill_no is not None:
            return self.bill_no
        else:
            return ""

class Book(models.Model):
    isbn = models.CharField(db_column='ISBN', unique=True, max_length=100, blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cover_url = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField()
    discount = models.FloatField()
    stock = models.IntegerField()
    num_pages = models.IntegerField()
    author = models.ForeignKey(Author)
    genre = models.ForeignKey('Genre')
    publisher = models.ForeignKey('Publisher')

    class Meta:
        managed = False
        db_table = 'tbl_book'

    def __str__(self):
        if self.isbn is not None and self.isbn.strip() != "":
            return self.isbn + " - " + self.title
        else:
            return self.title

    def __unicode__(self):
        return smart_unicode(self.title)

    def authors(self):
        return smart_unicode(self.author.name)

    def genres(self):
        return smart_unicode(self.genre.name)


class BookTag(models.Model):
    book = models.ForeignKey(Book)
    tag = models.ForeignKey('Tag')

    class Meta:
        managed = False
        db_table = 'tbl_book_tag'


class Customer(models.Model):
    username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=128, editable=False)
    fullname = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=45, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    ward = models.CharField(max_length=100, blank=True, null=True)
    street_number = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=45, blank=True, null=True)
    goodreads_id = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_customer'

    def __str__(self):
        if self.username is not None and self.fullname is not None:
            return self.username + " - " + self.fullname
        else:
            return ""

    def __unicode__(self):
        return smart_unicode(self.fullname)


class CustomerTag(models.Model):
    book = models.ForeignKey(Book, blank=True, null=True)
    customer = models.ForeignKey(Customer, blank=True, null=True)
    tag = models.ForeignKey('Tag', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_customer_tag'


class Friendship(models.Model):
    customer_a = models.ForeignKey(Customer, related_name='%(class)s_A', db_column='customer_a', blank=True, null=True)
    customer_b = models.ForeignKey(Customer, related_name='%(class)s_B', db_column='customer_b', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_friendship'


class Genre(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'tbl_genre'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return smart_unicode(self.name)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    snippet = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_tag'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return smart_unicode(self.name)


class OrderHistory(models.Model):
    STATUS_CHOICE = (
        (ORDER_STATUS_WAITING, 'Waiting'),
        (ORDER_STATUS_CONFIRMED, 'Confirmed And Shipping'),
        (ORDER_STATUS_COMPLETED, 'Completed'),
        (ORDER_STATUS_CANCEL, 'Cancel')
    )
    customer = models.ForeignKey(Customer, editable=False)
    order_date = models.DateTimeField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=False, choices=STATUS_CHOICE, default=1)
    total = models.FloatField(blank=True, default=0)
    shipping_fee = models.FloatField(blank=True, default=0)
    shipping_address = models.TextField(blank=True, null=True)
    shipping_phone = models.CharField(max_length=45, blank=True, null=True)
    shipping_fullname = models.CharField(max_length=255, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_order'

    def fullname(self):
        return self.customer.fullname

    def total_include_shipping(self):
        if self.shipping_fee is None:
            return self.total
        else:
            return self.shipping_fee + self.total

    def __str__(self):
        return "#" + self.id + " - " + self.order_date

    def __unicode__(self):
        return smart_unicode(self.id)

class OrderLine(models.Model):
    book = models.ForeignKey(Book)
    order_history = models.ForeignKey(OrderHistory)
    quantity = models.IntegerField(blank=True, null=True)
    unit_price = models.FloatField(blank=True, null=True)
    discount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_order_line'

class Publisher(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_publisher'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return smart_unicode(self.name)


class Recommendation(models.Model):
    customer = models.ForeignKey(Customer)
    book_recommend = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_recommendation'