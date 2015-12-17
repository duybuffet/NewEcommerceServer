import json
from models import *
from EcommerceAPI.constants import *
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from scripts import recommendation_algorithm as recommend_alg
from scripts import database_query_utility as db
from scripts import helper as help
from scripts.goodreads_api import key_secret, key, access_token_url, authorize_url, url, request_token_url, get_auth_user_id, get_user_books
import urlparse
from django.http import HttpResponse
import oauth2 as oauth


IMAGE_RELATIVE_PATH = "D:\PTIT Final\Source\BookEcommerceServer\EcommerceAPI\scripts"


def index(request):
    pass


def get_genres(request):
    if request.method == 'GET':
        data = db.get_all_genres()
        if len(data) > 0:
            return help.return_response(data, 200)
        else:
            data = {'error': 'Data not found'}
            return help.return_response(data, 404)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


def get_books(request):
    if request.GET.get('page'):
        page = int(request.GET.get('page'))
    else:
        page = 1

    if request.method == 'GET':
        response_data = {}
        response_data['page'] = page
        response_data['max_page'] = 'False'
        books = []

        pages = Paginator(db.get_all_book(), API_LIMIT_ELEMENT_PAGE)
        if page <= pages.num_pages and page > 0:
            books = pages.page(page).object_list
        else:
            response_data['max_page'] = 'True'
        response_data['books'] = books

        return help.return_response(response_data, 200)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


def get_book_by_id(request):
    book_id = request.GET.get('book_id')
    if request.method == 'GET':
        book = db.get_book_by_id(book_id)
        return help.return_response(book, 200)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


def get_books_by_genre(request):
    genre_id = request.GET.get("genre_id")
    if request.GET.get('page'):
        page = int(request.GET.get('page'))
    else:
        page = 1
    response_data = {}
    response_data['genre_id'] = genre_id
    response_data['max_page'] = 'False'
    books = []
    if request.method == 'GET':
        pages = Paginator(db.get_books_by_genre(genre_id), API_LIMIT_ELEMENT_PAGE)
        if page <= pages.num_pages and page > 0:
            books = pages.page(page).object_list
        else:
            response_data['max_page'] = 'True'

        response_data['books'] = books
        return help.return_response(response_data, 200)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


def get_new_books(request):
    if request.GET.get('page'):
        page = int(request.GET.get('page'))
    else:
        page = 1

    if request.method == 'GET':
        response_data = {}
        response_data['page'] = page
        response_data['max_page'] = 'False'
        books = []

        pages = Paginator(db.get_new_books(), API_LIMIT_ELEMENT_PAGE)
        if page <= pages.num_pages and page > 0:
            books = pages.page(page).object_list
        else:
            response_data['max_page'] = 'True'
        response_data['books'] = books
        return help.return_response(response_data, 200)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


def search_book(request):
    key_word = request.GET.get('key_word')
    search_type = request.GET.get('search_type')
    if request.GET.get('page'):
        page = int(request.GET.get('page'))
    else:
        page = 1

    if request.method == 'GET':
        response_data = {}
        response_data['search_type'] = search_type
        response_data['page'] = page
        response_data['max_page'] = 'False'
        books = []
        if search_type == API_KEYWORD_SEARCH_TYPE_TITLE:
            pages = Paginator(db.get_books_by_title(key_word), 30)
            if page <= pages.num_pages and page > 0:
                books = pages.page(page).object_list
            else:
                response_data['max_page'] = 'True'

            response_data['books'] = books
            return help.return_response(response_data, 200)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


@csrf_exempt
def log_in(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            customer = Customer.objects.filter(username=username, password=password).values("id")
            if len(customer) == 1:
                customer = db.get_customer_by_id(customer[0]["id"])
                data = {'success': 'Login Successfully',
                        'customer_login': customer}
                return help.return_response(data, 200)
            else:
                data = {'error': 'Login failed'}
                return help.return_response(data, 404)
        except Exception as inst:
            data = {'error': str(inst)}
            return help.return_response(data, 404)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            if len(Customer.objects.filter(username=username).values("id")) == 0:
                customer_new = Customer()
                customer_new.username = username
                customer_new.password = password
                customer_new.save()
                data = {'customer_register': {'id': customer_new.id}}
                return help.return_response(data, 200)
            else:
                data = {'error': 'Username exist'}
                return help.return_response(data, 404)
        except Exception as inst:
            data = {'error': str(inst)}
            return help.return_response(data, 404)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


@csrf_exempt
def handle_profile(request):
    if request.method == 'GET':
        customer_id = request.GET.get('customer_id')
        customer = db.get_customer_by_id(customer_id)
        return help.return_response(customer, 200)
    elif request.method == 'POST':
        print('Request body : %s' % request.body)
        customer_id = request.POST.get('customer_id')
        print("Customer ID : %s" % customer_id)
        customer_update = Customer.objects.get(pk=customer_id)
        if customer_update is None:
            data = {'error': 'Data not found'}
            return help.return_response(data, 404)
        else:
            try:
                customer_update.fullname = request.POST.get('fullname')
                customer_update.city = request.POST.get('city')
                customer_update.ward = request.POST.get('ward')
                customer_update.email = request.POST.get('email')
                customer_update.phone = request.POST.get('phone')
                customer_update.street_number = request.POST.get('street_number')
                customer_update.district = request.POST.get('district')
                customer_update.postal_code = request.POST.get('postal_code')
                customer_update.save()
                data = {'Success': 'Change profile successfully!'}
                return help.return_response(data, 200)
            except Exception:
                data = {'error': 'Change profile failed'}
                return help.return_response(data, 404)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


@csrf_exempt
def handle_order(request):
    if request.method == 'GET':
        order_id = request.GET.get('order_id')
        order = db.get_order_by_id(order_id)
        return help.return_response(order, 200)
    elif request.method == 'POST':
        if add_order(request):
            data = {'success': 'Add order successfully'}
            return help.return_response(data, 200)
        else:
            data = {'error': 'Add order failed'}
            return help.return_response(data, 404)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


def add_order(request):
    try:
        order = OrderHistory()
        order.status = ORDER_STATUS_WAITING
        order.customer = Customer.objects.get(id=request.POST.get('customer_id'))
        order.shipping_address = request.POST.get('shipping_address')
        order.shipping_fullname = request.POST.get('shipping_fullname')
        order.shipping_phone = request.POST.get('shipping_phone')
        order.total = request.POST.get('total')
        order.note = request.POST.get('note')
        order.order_date = timezone.now()
        order.save()
        order_id = order.id
        for line in json.loads(request.POST.get('list_item')):
            order_line = OrderLine()
            order_line.quantity = line['quantity']
            order_line.unit_price = line['book']['price']
            order_line.discount = line['book']['discount']
            order_line.book = Book.objects.get(pk=line['book']['id'])
            order_line.order_history = OrderHistory.objects.get(pk=order_id)
            order_line.save()
        return True
    except Exception as inst:
        print "EXCEPTION: %s" % inst
        return False


def get_orders_by_customer(request):
    if request.method == 'GET':
        data = db.get_orders_by_customer(request.GET.get('customer_id'))
        return help.return_response(data, 200)
    else:
        data = {'error': 'Data not found'}
        return help.return_response(data, 404)


CONSUMERS = {}


def request_oauth(request):
    if request.method == 'GET':
        consumer = oauth.Consumer(key=key, secret=key_secret)
        client = oauth.Client(consumer)
        response, content = client.request(request_token_url, 'GET')
        if response['status'] != '200':
            raise Exception('Invalid response: %s, content: ' % response['status'] + content)
        request_token = dict(urlparse.parse_qsl(content))
        authorize_link = '%s?oauth_token=%s' % (authorize_url, request_token['oauth_token'])
        CONSUMERS[request_token['oauth_token_secret']] = consumer

        data = {'request_url': authorize_link, 'oauth_token': request_token['oauth_token'],
            'oauth_token_secret': request_token['oauth_token_secret']}

        return help.return_response(data, 200)
    else:
        data = {'error': 'Cannot get authorize url'}
        return help.return_response(data, 404)
    # return help.return_response({},200)


def oauth_user(request):
    token = request.GET.get('oauth_token')
    token_secret = request.GET.get('oauth_token_secret')
    consumer = oauth.Consumer(key=key, secret=key_secret)
    token = oauth.Token(token, token_secret)

    client = oauth.Client(consumer, token)
    response, content = client.request(access_token_url, 'POST')
    if response['status'] != '200':
        raise Exception('Invalid response: %s' % response['status'])

    access_token = dict(urlparse.parse_qsl(content))
    #
    # this is the token you should save for future uses
    # print 'Save this for later: '
    # print 'oauth token key:    ' + access_token['oauth_token']
    # print 'oauth token secret: ' + access_token['oauth_token_secret']
    #
    token = oauth.Token(access_token['oauth_token'],
                        access_token['oauth_token_secret'])
    #
    return oauth.Client(consumer, token)
    # return help.return_response({},200)


def get_books_by_recommendation(request):
    client = oauth_user(request)
    id = get_auth_user_id(client)
    data = recommend_alg.recommend_book(get_user_books(id, client), recommend_alg.select_candidate_set(id, client), client)
    if data is not None:
        help.return_response(data, 200)
    else:
        data = {'error': 'not having recommend'}
    return help.return_response(data, 200)


def get_image(request):
    try:
        mime_type = ""
        flag = True
        real_path = request.REQUEST.get('cover_url')
        if real_path:
            mime_type = get_mime_type(real_path)
        else:
            flag = False
    except:
        flag = False

    if flag:
        return HttpResponse(open(IMAGE_RELATIVE_PATH + real_path,'rb'), content_type=mime_type, status=200)
    else:
        data = {'error': 'Cannot get authorize url'}
        return help.return_response(data, 404)


def get_mime_type(real_path):
    mime_type = ""
    if real_path.endswith(".jpg") | real_path.endswith(".jpeg"):
        mime_type = "image/jpeg"
    elif real_path.endswith(".png"):
        mime_type = "image/png"
    elif real_path.endswith(".bm") | real_path.endswith(".bmp"):
        mime_type = "image/bmp"
    elif real_path.endswith(".gif"):
        mime_type = "image/gif"
    elif real_path.endswith(".ico"):
        mime_type = "image/x-icon"
    else:
        mime_type = "application/force-download"
    return mime_type