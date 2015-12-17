import time
import oauth2 as oauth
import urlparse
import xml.etree.ElementTree as ET
import database_query_utility as db


__author__ = 'Duy'


url = 'http://www.goodreads.com'
request_token_url = '%s/oauth/request_token' % url
authorize_url = '%s/oauth/authorize' % url
access_token_url = '%s/oauth/access_token' % url
NONE_SEMENTIC_SHELVES = ['to-read','read','currently-reading','books-i-own','owned-books', 'favorites', 'ya',
                         'favorite', '5-stars', '-mine-', 'sci-fi', 'scifi', 'sci-fi-fantasy', 'self-help',
                         'alwaysreading', 'no-ebook', 'in-stock-at-our-store', 'saw-as-a-movies', 'all-time-favorites',
                         'to-buy', 'on-writing', 'default', 'reference', 'proposed-reading-program', 'non-fic',
                         'saw-as-a-movies', 'nonfiction-to-read', 'books-about-books', 'loc_med_26', 'to-get',
                         'done-reading', 'scifi-fantasy', 'books-unexamined', 'on-the-shelf', 'to-be-filed', 'sf',
                         'tbr-general', 'self-help', 'd-e-a-r-pd-books', 'to-read-non-fiction', 'to-read-plays',
                         'need-to-buy', 'saw-as-a-movies', 'to-read-teaching-books', 'sf', 'on-the-shelf',
                         'done-reading', 'withdrawn-fr-bvtn-city-library','ya-middle-school', '1', 'purchased', 'how-to',
                         'unread', 'myshelf', '1001-books-to-read-before-you-die', 'of']
key = 'yVIPvj6gnA7CcNnUbcdynQ'
key_secret = 'pJcV7WJzv8KSJfZeQ2FlMwSxCBCPQ6HQKxODF6IRytA'


def get_client():
    consumer = oauth.Consumer(key=key,
                              secret=key_secret)
    client = oauth.Client(consumer)
    response, content = client.request(request_token_url, 'GET')
    if response['status'] != '200':
        raise Exception('Invalid response: %s, content: ' % response['status'] + content)

    request_token = dict(urlparse.parse_qsl(content))

    authorize_link = '%s?oauth_token=%s' % (authorize_url,
                                            request_token['oauth_token'])
    print "Use a browser to visit this link and accept your application:"
    print authorize_link
    accepted = 'n'
    while accepted.lower() == 'n':
        # you need to access the authorize_link via a browser,
        # and proceed to manually authorize the consumer
        accepted = raw_input('Have you authorized me? (y/n) ')

    token = oauth.Token(request_token['oauth_token'],
                        request_token['oauth_token_secret'])

    client = oauth.Client(consumer, token)
    response, content = client.request(access_token_url, 'POST')
    if response['status'] != '200':
        raise Exception('Invalid response: %s' % response['status'])

    access_token = dict(urlparse.parse_qsl(content))

    # this is the token you should save for future uses
    print 'Save this for later: '
    print 'oauth token key:    ' + access_token['oauth_token']
    print 'oauth token secret: ' + access_token['oauth_token_secret']

    token = oauth.Token(access_token['oauth_token'],
                        access_token['oauth_token_secret'])

    return oauth.Client(consumer, token)

# client = get_client()

def get_auth_user_id(client):
    response, content = client.request('%s/api/auth_user' % url,'GET')
    if response['status'] != '200':
        raise Exception('Cannot fetch resource: %s' % response['status'])
    root = ET.fromstring(content)
    return str(root[1].get('id'))


def get_user_friends(auth_user_id, client):
    list_friend = []
    response, content = client.request('%s/friend/user/%s?format=xml' % (url, auth_user_id), 'GET')
    if response['status'] != '200':
        raise Exception('Cannot fetch resource: %s' % response['status'])

    root = ET.fromstring(content)
    [list_friend.append(user[0].text) for user in root[1]]
    return list_friend


def get_user_followings(auth_user_id, client):
    list_follow = []
    response, content = client.request('%s/user/%s/following.xml?key=%s' % (url, auth_user_id, key), 'GET')
    if response['status'] != '200':
        raise Exception('Cannot fetch resource: %s' % response['status'])
    else:
        root = ET.fromstring(content)
        [list_follow.append(user.find('id').text) for user in root.find('following')]
    return list_follow


def get_user_books(user_id, client):
    list_book = []
    response, content = client.request('%s/review/list.xml?v=2&id=%s&shelf=all' % (url, user_id), 'GET')
    if response['status'] != '200':
        # raise Exception('Cannot fetch resource: %s' % response['status'])
        print "Cannot fetch resource"
        pass
    else:
        root = ET.fromstring(content)
        for review in root.find('reviews'):
            list_shelf = []
            [list_shelf.append(shelf.get('name')) if shelf.get('name') not in NONE_SEMENTIC_SHELVES else list_shelf for shelf in review.find('shelves')]
            isbn = ''
            if review.find('book').find('isbn') != None:
                isbn = review.find('book').find('isbn').text
            list_book.append({'book_id' : review.find('book').find('id').text,'isbn': isbn , 'list_shelf' : list_shelf,
                              'title': review.find('book').find('title').text})
    return list_book


def get_user_book_shelves(user_id, book_id, client):
    list_shelf = []
    response, content = client.request('%s/review/list.xml?v=2&id=%s&shelf=all' % (url, user_id), 'GET')
    if response['status'] != '200':
        raise Exception('Cannot fetch resource: %s' % response['status'])
    else:
        root = ET.fromstring(content)
        for review in root.find('reviews'):
            if book_id == review[1][0].text:
                for shelf in review[6]:
                    if shelf.get('name') not in NONE_SEMENTIC_SHELVES: list_shelf.append(shelf.get('name'))
                # [list_shelf.append(shelf.get('name')) for shelf in review[6]]
    return list_shelf


def get_shelves_of_user(id, client):
    list_shelves = []
    response, content = client.request('%s/shelf/list.xml?user_id=%skey=%s' % (url, id, key), 'GET')
    if response['status'] != '200':
        pass

    root = ET.fromstring(content)
    for shelf in root[1]:
        name = shelf[1].text.lower()
        if name not in NONE_SEMENTIC_SHELVES : list_shelves.append(name)

    return list_shelves


def get_friends_books(list_friend, client):
    print "list friend: %s"%list_friend
    list_friends_books = []
    for friend_id in list_friend:
        response, content = client.request('%s/review/list.xml?v=2&id=%s&shelf=all' % (url, friend_id), 'GET')
        if response['status'] != '200':
            # raise Exception('Cannot fetch resource: %s' % response['status'])
            continue
        root = ET.fromstring(content)
        list_book = []
        for review in root[1]:
            list_shelf = []
            for shelf in review[6]:
                if shelf.get('name') not in NONE_SEMENTIC_SHELVES: list_shelf.append(shelf.get('name'))
            # [list_shelf.append(shelf.get('name')) for shelf in review[6]]
            list_book.append({review[1][0].text : list_shelf})
        print "list book: %s"%list_book
        list_friends_books.append({friend_id : list_book})
    return list_friends_books


def get_shelves_of_book_on_cloud(book_id, client):
    list_shelf = []
    response, content = client.request('%s/book/show/%s?format=xml&key=%s' % (url, book_id, key), 'GET')
    if response['status'] != '200':
        # raise Exception('Cannot fetch resource: %s' % response['status'])
        pass
    else:
        try:
            root = ET.fromstring(content)
            # print "root : %s"%root.find('book').find('popular_shelves')
            if root.find('book').find('popular_shelves') is not None:
                for shelf in root.find('book').find('popular_shelves'):
                    name = shelf.get('name').lower()
                    if name not in NONE_SEMENTIC_SHELVES: list_shelf.append(name)
        except:
            # raise Exception('Cannot fetch resource: %s' % response['status'])
            pass
    return list_shelf


def get_book(book_id, client):
    res = {}
    try:
        response, content = client.request('%s/book/show/%s?format=xml&key=%s' % (url, book_id, key), 'GET')
        root = ET.fromstring(content)
        book = root.find('book')
        authors = []
        shelves = []
        for author in book.find('authors'):
            authors.append({'id': author.find('id').text, 'name': author.find('name').text})
        for shelf in book.find('popular_shelves'):
            name = shelf.get('name')
            if (name) not in NONE_SEMENTIC_SHELVES:
                shelves.append(name)

        res = {"id": book.find('id').text,
               "isbn": book.find('isbn').text,
               "title": book.find('title').text,
               "cover_url": book.find('image_url').text,
               "description": book.find('description').text,
               "num_pages": book.find('num_pages').text,
               "authors": authors,
               "shelves": shelves
               }
    except Exception:
        pass
    return res


# start = time.clock()
#
#
# _client = get_client()
# user_id = get_auth_user_id(_client)
# followings = get_user_followings(user_id, _client)
# friends = get_user_friends(user_id, _client)
# list_user = followings + friends
# for frd in list_user:
#     user_b = db.get_customer_by_goodreads_id(frd)
#     print "user_b : %s"%user_b['id']
#     if db.is_friend(5, user_b['id']):
#         continue
#     else:
#         db.make_friend(5, user_b['id'])

# for frd_fl in ['46109817']:
#     customer = db.get_customer_by_goodreads_id(frd_fl)
#     user_books = get_user_books(frd_fl, _client)
#     for u_book in user_books:
#         if (u_book['isbn'] is not None and u_book['isbn'] != None and u_book['isbn'] != ""):
#             book = db.get_book_by_isbn(u_book['isbn'])
#         else:
#             book = db.get_book_by_title(u_book['title'])
#         if book == None:
#             insert_book = db.insert_book_to_db(get_book(u_book['book_id'], _client))
#             book_id = insert_book.id
#         else:
#             book_id = book['id']
#         for tag in u_book['list_shelf']:
#             try:
#                 db.insert_book_tag_of_customer(customer['id'],book_id, tag)
#             except:
#                 continue


# print get_shelves_of_book_on_cloud(631932, client)
# _client = get_client()
# print "following: %s"%followings
# print "friends: %s"%friends
# print "list_user: %s"%list_user
# print get_user_followings(user_id, _client)
# print get_user_friends(user_id, _client)
# print get_user_books(user_id, _client)
# print(get_friends_books(get_user_friends(user_id, _client), _client))
# print get_shelves_of_book_on_cloud(22,_client)
# print get_shelves_of_user(46199325)
# print get_book(75)
# print "Spending time : %s" % (time.clock() - start)