from django.core.wsgi import get_wsgi_application
from EcommerceAPI.models import *
from django.core.paginator import Paginator
from EcommerceAPI.constants import *
from django.db.models import Q
from random import randint
from django.db.models import Count
from django.db.models.functions import *
import os
import sys
import logging
import word_similarity_algorithm as wa
import helper

parentdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parentdir)

env = "BookEcommerce.settings"
strip_list = ['<p>', '</p>', '<em>', '</em>', '<b>', '</b>', '<br>', '<br/>']

# setup_environ(settings)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", env)

application = get_wsgi_application()

__author__ = 'duy'


# BOOK API

def get_all_genres():
    result = []
    genres = Genre.objects.all()
    for gen in genres:
        result.append({"id": gen.id, "name": gen.name})
    return result


def convert_cover(url):
    """
    convert url
    :param date: string
    :return:string
    """
    print "url : %s"%url
    if url.strip() == "" or url is None:
        url = "https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png"
    # else:
    #     url = url.replace('\r','')
    #     url = url.replace('\n','')
    return url


def get_new_books():
    """
    search book new limit 10
    :return: list object Book
    """
    filters = Q()
    books = Book.objects.filter(filters).order_by('id').reverse().values('id', 'title', 'cover_url', 'discount', 'stock', 'price')[:API_LIMIT_ELEMENT_SEARCH]
    list_book = []
    for book in books:
        data = {'id': book['id'], 'title': book['title'], 'cover_url': book['cover_url'], 'discount': book['discount'], 'stock': book['stock'], 'price': book['price']}
        list_book.append(data)
    return list_book


def get_books_by_title(key_word):
    """
    search book by title book
    :param key_word: key word title
    :return:list object Book
    """
    filters = Q(title__icontains = key_word)
    books = Book.objects.filter(filters).values('id', 'title', 'cover_url')
    list_book = []
    for book in books:
        data = {'id': book['id'], 'title': book['title'], 'cover_url': book['cover_url']}
        list_book.append(data)
    return list_book


def get_books_by_genre(genre_id):
    """
    Get list of books that have genre_id
    :param genre_id:
    :return: list books having genre_id
    """
    result = []
    try:
        list_book_id = BookGenre.objects.filter(genre_id = genre_id).values("book_id")
        list_id = []
        for id in list_book_id:
            list_id.append(id['book_id'])

        list_book = Book.objects.filter(pk__in = list_id).values('id', 'title', 'cover_url', 'price', 'stock',
                                                                 'discount')

        for book in list_book:
            result.append({'id': book['id'], 'title': book['title'], 'cover_url': book['cover_url'],
                           'price': book['price'], 'stock': book['stock'], 'discount': book['discount']})
        return result
    except Exception as inst:
        logging.error(type(inst))
        logging.error(inst)
        return []


def get_all_book():
    """
    get id and title of All book
    :return: list object book
    """
    filters = Q()
    books = Book.objects.filter(filters).values('id', 'title', 'cover_url', 'discount', 'stock', 'price')
    list_book = []
    for book in books:
        title = helper.smart_truncate(book['title'], 60)
        data = {'id': book['id'], 'title': title, 'cover_url': book['cover_url'], 'discount': book['discount'], 'stock': book['stock'], 'price': book['price']}
        list_book.append(data)
    return list_book


def get_book_by_id(book_id):
    list_author = []
    list_genre = []

    for genre in BookGenre.objects.filter(book__id=book_id).values("genre_id"):
        list_genre.append(Genre.objects.filter(id=genre['genre_id']).values("name")[0]["name"])

    for author in BookAuthor.objects.filter(book__id=book_id).values("author_id"):
        list_author.append(Author.objects.filter(id=author['author_id']).values("name")[0]["name"])

    filters = Q(id=book_id)
    book = Book.objects.filter(filters).values("id", "isbn",
                                               "cover_url", "title",
                                               "description", "price",
                                               "discount", "stock",
                                               "num_pages")
    data = {}
    if  len(book) > 0:
        data = {"id" : book[0]["id"], "cover_url": book[0]["cover_url"], "description": book[0]["description"],
                "discount": book[0]["discount"], "num_pages": book[0]["num_pages"], "stock": book[0]["stock"],
                "isbn": book[0]["isbn"], "title": book[0]["title"], "price": book[0]["price"],
                "author": list_author, "genre": list_genre}
    return data


# CUSTOMER API

def get_customer_by_id(customer_id):
    customer = Customer.objects.filter(id=customer_id).values("id", "fullname", "email", "phone",
                                                              "city", "district", "ward",
                                                              "street_number", "postal_code")
    if len(customer) > 0:
        data = {"id": customer[0]["id"], "fullname": customer[0]["fullname"], "email": customer[0]["email"],
                "phone": customer[0]["phone"], "city": customer[0]["city"], "district": customer[0]["district"],
                "ward": customer[0]["ward"], "street_number": customer[0]["street_number"],
                "postal_code": customer[0]["postal_code"]}
    return data


def get_order_by_id(order_id):
    list_item = []
    order_lines = OrderLine.objects.filter(order_history__id=order_id).values("book_id", "quantity")
    for line in order_lines:
        line_details = {"quantity": line["quantity"]}
        book = Book.objects.get(pk=line["book_id"])
        if book is None:
            line_details["title"] = ""
        else:
            line_details["title"] = book.title
        list_item.append(line_details)

    order = OrderHistory.objects.filter(pk=order_id).values("id", "status", "shipping_fee", "total", "order_date", "note")
    if len(order) > 0:
        data = {"id": order_id, "status": order[0]["status"], "shipping_fee": order[0]["shipping_fee"],
                "total": order[0]["total"], "order_date": unicode(order[0]["order_date"].strftime("%d/%m/%Y %H:%M:%S")),
                "list_item": list_item, "note": order[0]["note"]}
        return data
    return {}


def get_orders_by_customer(customer_id):
    orders = OrderHistory.objects.filter(customer__id=customer_id).values("id", "status", "total", "order_date").reverse()
    data = []
    for order in orders:
        data.append({"id": order["id"], "status": order["status"],
                "total": order["status"], "order_date": unicode(order["order_date"].strftime("%d/%m/%Y %H:%M:%S"))})
    result = {"orders": data}
    return result


# RECOMMENDATION ALGORITHM

def get_customer_tags_of_book(book_id, customer_id):
    result = []
    customer_tags = CustomerTag.objects.filter(book__id=book_id,customer__id=customer_id,).values('tag__name')
    [result.append(customer_tag['tag__name']) for customer_tag in customer_tags]
    return result


def get_friends_of_customer(customer_id):
    result = []
    friends = Friendship.objects.filter(customer_a=customer_id).values('customer_b')
    [result.append(fr['customer_b']) for fr in friends]
    friends = Friendship.objects.filter(customer_b=customer_id).values('customer_a')
    [result.append(fr['customer_a']) for fr in friends]
    return result


def get_books_of_customer(customer_id):
    result = []
    customer_books = CustomerTag.objects.filter(customer__id=customer_id).values('book_id').distinct()
    [result.append(c_book['book_id']) for c_book in customer_books]
    return result


def get_book_by_isbn(isbn):
    if isbn is None: return None
    result = Book.objects.filter(isbn=isbn).values('id', 'isbn')
    print "result: %s"%result
    if len(result) > 0:
        return result[0]
    return None


def get_book_by_title(title):
    if title is None: return None
    result = Book.objects.filter(title=title).values('id')
    print "result in get book by title: %s"%result
    if len(result) > 0:
        return result[0]
    return None


def get_popular_tag_of_book(book_id):
    result = []
    book_tags = BookTag.objects.filter(book__id=book_id).values('tag__name')
    [result.append(b_tag['tag__name']) for b_tag in book_tags]
    return result


# print get_popular_tag_of_book(50)
# print get_books_of_customer(5)
# print get_friends_of_customer(1)
# print get_customer_tag_of_book(50,5)
def insert_book_to_db(book):
    insert_book = Book()
    try:
        # insert_books = Book.objects.filter(isbn = book["isbn"])
        # if (len(insert_books) == 0):
        # insert_book = insert_books[0]
        insert_book.cover_url = convert_cover(book["cover_url"])
        insert_book.isbn = book["isbn"]
        insert_book.description = book["description"]
        for strip_item in strip_list:
            if insert_book.description != "" and insert_book.description != None:
                insert_book.description = insert_book.description.replace(strip_item, "")

        insert_book.num_pages = book["num_pages"]
        insert_book.title = book["title"]
        insert_book.price = randint(30,300)
        insert_book.stock = randint(0, 100)
        insert_book.discount = 0
        insert_book.save()

        for a in book["authors"]:
            author_s = Author.objects.filter(id = a["id"])
            if len(author_s) > 0:
                author = author_s[0]
            else:
                author = Author()
                author.id = a["id"]
                author.name = a["name"]
                author.save()
            book_author = BookAuthor()
            book_author.author = author
            book_author.book = insert_book
            book_author.save()

        for s in book["shelves"]:
            tag_s = Tag.objects.filter(name = s)
            if len(tag_s) > 0:
                tag = tag_s[0]
            else:
                tag = Tag()
                tag.name = s
                tag.save()
            book_tag = BookTag()
            book_tag.tag = tag
            book_tag.book = insert_book
            book_tag.save()
    except Exception as inst:
        # print(inst.message)
        pass
    print "insert book success"
    return insert_book
#

def insert_book_tag_of_customer(customer_id, book_id, tag_name):
    result = Tag.objects.filter(name=tag_name).values('id')
    if len(result) > 0:
        tag_id = result[0]['id']
        if len(CustomerTag.objects.filter(customer__id=customer_id, book__id=book_id, tag__id=tag_id)) > 0:
            return
    else:
        tag = Tag()
        tag.name = tag_name
        tag.save()
        tag_id = tag.id
    customer_tag = CustomerTag()
    customer_tag.tag = Tag.objects.get(id=tag_id)
    customer_tag.book = Book.objects.get(id=book_id)
    customer_tag.customer = Customer.objects.get(id=customer_id)
    customer_tag.save()
    print "insert customer_tag success ==== id: %s"%customer_tag.id


def get_customer_by_goodreads_id(goodreads_id):
    result = Customer.objects.filter(goodreads_id=goodreads_id).values('id')
    if len(result) > 0:
        customer = result[0]
        print "customer: %s"%customer
    else:
        customer = Customer()
        customer.goodreads_id = goodreads_id
        customer.save()
        print "insert customer success: %s - id: %s"%(customer, customer.id)
        return Customer.objects.filter(id=customer.id).values('id')
    return customer


def is_friend(u_id_1, u_id_2):
    fr = Friendship.objects.filter(
        Q(customer_a__id=u_id_1, customer_b__id=u_id_2) | Q(customer_b__id=u_id_1, customer_a__id=u_id_2)
    )
    if len(fr) > 0:
        return True
    return False


def make_friend(u_id_1, u_id_2):
    fr = Friendship()
    fr.customer_a = Customer.objects.get(id=u_id_1)
    fr.customer_b = Customer.objects.get(id=u_id_2)
    fr.save()


def insert_snippet_of_tag(tag_name):
    tag = Tag.objects.get(name=tag_name)
    # if tag.snippet == "":
    snippet = wa.get_handle_snippet(tag_name)
    tag.snippet = snippet
    tag.save()
    print "insert %s success"%tag_name


# list_tag = Tag.objects.filter(id__gte=4849)
# for tag in list_tag:
#     try:
#         insert_snippet_of_tag(tag.name)
#     except:
#         print "Error at"
# print( insert_snippet_of_tag("fiction"))
# print is_friend(14, 13)
# print insert_book_tag_of_customer(15,48,"fiction")
# book = {'isbn': '0352272395', 'description': '<strong>What John McPhee\'s books all have in common is that they are about real people in real places. Here, at his adventurous best, he is out and about with people who work in freight transportation.</strong><br><br><br>Over the past eight years, John McPhee has spent considerable time in the company of people who work in freight transportation. <em>Uncommon Carriers </em>is his sketchbook of them and of his journeys with them. He rides from Atlanta to Tacoma alongside Don Ainsworth, owner and operator of a sixty-five-foot,<br>eighteen-wheel chemical tanker carrying hazmats. McPhee attends ship-handling school on a pond in the foothills of the French Alps, where, for a tuition of $15,000 a week, skippers of the largest ocean ships refine their capabilities in twenty-foot scale models. He goes up the "tight-assed" Illinois River on a<br>"towboat" pushing a triple string of barges, the overall vessel being "a good deal longer than the <em>Titanic</em>." And he travels by canoe up the canal-and-lock commercial waterways traveled by Henry David Thoreau and his brother, John,<br>in a homemade skiff in 1839.<br><br><em>Uncommon Carriers </em>is classic work by McPhee, in prose distinguished, as always, by its author\'s warm humor, keen insight, and rich sense of human character.', 'title': 'Uncommon Carriers', 'num_pages': '256', 'authors': [{'id': '40', 'name': 'John McPhee'}], 'id': '75', 'cover_url': 'http://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png', 'shelves': ['non-fiction', 'nonfiction', 'essays', 'travel', 'business', 'transportation', 'history', 'economics']}
# for id in range(5500,6000):
#     try:
#         print "id : %s"%id
#         book = gr.get_book(id)
#         print book
#         insert_book_to_db(book)
#     except Exception as inst:
#         print inst.message
#         continue

# print Book.objects.get(id=16)
# print get_book_by_isbn(None)
