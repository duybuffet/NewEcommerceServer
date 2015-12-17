__author__ = 'Duy'
import time
import os
from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'BookEcommerce.settings'
application = get_wsgi_application()
from EcommerceAPI.models import *
# import goodreads_api as gr_api
import word_similarity_algorithm as similar_alg
import database_query_utility as db
import operator


# def resem(source_book_id, candidate_book_id, client):
#     # can improve get_shelves_of_book_on_cloud by insert shelves to the local db
#
#     sb_shelves = gr_api.get_shelves_of_book_on_cloud(source_book_id, client)
#     # print "sb_shelves : %s"%sb_shelves
#     cb_shelves = gr_api.get_shelves_of_book_on_cloud(candidate_book_id, client)
#     # print "cb_shelves: %s"%cb_shelves
#
#     total_min = 0
#     for sb in sb_shelves:
#         total_similar = 0
#         for cb in cb_shelves:
#             # total_similar += similar_alg.similarity_measure(sb, cb)
#             if sb == cb:
#                 sim = 1
#             else:
#                 sim = similar_alg.similarity_measure(sb, cb)
#             total_similar += sim
#             print "sim between %s and %s : %s" %(sb, cb, sim)
#         total_min += min(total_similar, 1)
#     return total_min


# def close(sb_gr_shelves, gr_friend_id, client):
#     # sb_gr_shelves = gr_api.get_user_book_shelves(gr_api.get_auth_user_id(), source_book_id)
#     print "sb_gr : %s" % sb_gr_shelves
#     gr_friend_shelves = gr_api.get_shelves_of_user(gr_friend_id, client)
#
#     total_min = 0
#     for sb in sb_gr_shelves:
#         total_similar = 0
#         for gr in gr_friend_shelves:
#             # total_similar += similar_alg.similarity_measure(sb, gr)
#             sim = similar_alg.similarity_measure(sb, gr)
#             total_similar += sim
#             print "sim between shelf %s and friend_%s : %s" %(sb, gr, sim)
#         total_min += min(total_similar, 1)
#         print "min : %s" % min(total_similar, 1)
#     return total_min


# def select_candidate_set(auth_user_id, client):
#     auth_user_shelves = set(gr_api.get_shelves_of_user(auth_user_id, client))
#     auth_user_friends = gr_api.get_user_friends(auth_user_id, client)
#     auth_user_friends_with_shelves = []
#     result_with_len = []
#     candidate = []
#
#     for frd in auth_user_friends:
#         auth_user_friends_with_shelves.append({"friend_id": frd, "list_shelves": gr_api.get_shelves_of_user(frd, client)})
#
#     for friends_shelves in auth_user_friends_with_shelves:
#         length_friend_shelves = len(set(friends_shelves["list_shelves"]))
#         if length_friend_shelves > 0:
#             intersect_length = len(auth_user_shelves.intersection(set(friends_shelves["list_shelves"])))
#
#             if (intersect_length > 0):
#                 ratio = float(intersect_length) / length_friend_shelves
#                 result = {"ratio": ratio,
#                     "friend_id": friends_shelves["friend_id"]}
#                 print "ratio : %s"%ratio
#                 result_with_len.append(result)
#             else:
#                 continue
#         else:
#             continue
#     result_with_len.sort(key=operator.itemgetter('ratio'), reverse=True)
#
#     if len(result_with_len) > 5:
#         for res in result_with_len[0:5]:
#             candidate.append({"friend_id": res["friend_id"], "book_ids": gr_api.get_user_books(res["friend_id"], client)})
#     else:
#         for res in result_with_len:
#             candidate.append({"friend_id": res["friend_id"], "book_ids": gr_api.get_user_books(res["friend_id"], client)})
#
#     # return [{"book_id" : 1234, "friend_id" : 4567}]
#     return candidate


# def recommend_book(list_book_in_profile, candidate_set, client):
#     list_recommended_book = []
#     ranking_for_each_book = []
#
#     for user_book in list_book_in_profile:
#         for candidate in candidate_set:
#             interest_degree = close(user_book.get('list_shelf'), candidate.get('friend_id'), client)
#             for book in candidate.get('book_ids'):
#                 resem_degree = resem(user_book, book.get('book_id'), client)
#                 rank_point = resem_degree * interest_degree
#                 ranking_for_each_book.append({'book_id': book, 'rank_point': rank_point})
#
#     ranking_for_each_book.sort(key=operator.itemgetter('rank_point'), reverse=True)
#     if len(ranking_for_each_book) > 10:
#         for res in ranking_for_each_book[0:10]:
#             list_recommended_book.append(res['book_id'])
#     else:
#         for res in ranking_for_each_book:
#             list_recommended_book.append(res['book_id'])
#     return list_recommended_book


def resem_ver_db(source_book_id, candidate_book_id):
    print "################ RESEM MODULE ################"
    sb_tags = Book.objects.get(id = source_book_id).booktag_set.all()
    cb_tags = Book.objects.get(id = candidate_book_id).booktag_set.all()

    total_min = 0
    for sb in sb_tags:
        total_similar = 0
        for cb in cb_tags:
            if sb.tag.name == cb.tag.name:
                sim = 1
                print "sim between %s and %s : overlap" %(sb.tag.name, cb.tag.name)
            else:
                sim = similar_alg.similarity_measure_ver_db(sb.tag.name, cb.tag.name, 'cosine')
            total_similar += sim
            print "sim between %s and %s : %s" %(sb.tag.name.encode("utf-8"), cb.tag.name.encode("utf-8"), sim)
        total_min += min(total_similar, 1)
    return total_min


def close_ver_db(sb_gr_tags, gr_friend_id):
    print "################ CLOSE MODULE ################"
    gr_friend_tags = Customer.objects.get(id = gr_friend_id).customertag_set.all()
    print "gr_friend_tags len: %s"%len(gr_friend_tags)
    total_min = 0
    for sb in sb_gr_tags:
        total_similar = 0
        for gr in gr_friend_tags:
            sim = similar_alg.similarity_measure_ver_db(sb, gr.tag.name, 'cosine')
            total_similar += sim
        total_min += min(total_similar, 1)
        print "min : %s" % min(total_similar, 1)
    return total_min


def select_candidate_set_for_book_ver_db(book, customer):
    print "################ CANDIDATE ################"
    auth_user_tags = set(db.get_customer_tags_of_book(book, customer))
    if len(auth_user_tags) == 0:
        auth_user_tags = set(db.get_popular_tag_of_book(book))
    else:
        pass

    auth_user_friends = db.get_friends_of_customer(customer)
    print "===auth_user_friends: %s"%auth_user_friends
    auth_user_friends_with_books = []
    candidate = []

    for frd in auth_user_friends:
        auth_user_friends_with_books.append({'friend_id': frd, 'list_books': db.get_books_of_customer(frd)})
    # print "===auth_user_friends_with_books: %s"%auth_user_friends_with_books
    for friends_books in auth_user_friends_with_books:
        for f_book in friends_books['list_books']:
            if f_book == book:
                print "=== overlap"
                continue
            else:
                f_book_tags = db.get_customer_tags_of_book(f_book, friends_books['friend_id'])
                length_friend_tags = len(f_book_tags)
                if length_friend_tags > 0:
                    intersect = len(auth_user_tags.intersection(set(f_book_tags)))
                    if intersect > 0:
                        candidate.append({'book_id': f_book, 'friend_id': friends_books['friend_id'], 'intersect': intersect})
                    else:
                        continue
                else:
                    continue
    candidate.sort(key=operator.itemgetter('intersect'), reverse=True)
    print "candidate: %s"%candidate
    return candidate


def recommend_book_ver_db(customer, N):
    list_recommended_book = []
    ranking_for_each_book = []
    list_book_in_profile = db.get_books_of_customer(customer)

    for user_book in list_book_in_profile:
        for candidate in select_candidate_set_for_book_ver_db(user_book, customer):
            resemblance_degree = resem_ver_db(user_book, candidate['book_id'])
            if resemblance_degree > 0:
                interest_degree = close_ver_db(db.get_customer_tags_of_book(user_book, customer), candidate['friend_id'])
                rank_point = resemblance_degree * interest_degree
                ranking_for_each_book.append({'book_id': candidate['book_id'], 'rank_point': rank_point})
            else:
                continue
    ranking_for_each_book.sort(key=operator.itemgetter('rank_point'), reverse=True)
    print "ranking for each book: %s"%ranking_for_each_book
    if len(ranking_for_each_book) > N:
        for res in ranking_for_each_book[0:N]:
            list_recommended_book.append(res['book_id'])
    else:
        for res in ranking_for_each_book:
            list_recommended_book.append(res['book_id'])
    return list_recommended_book


# start = time.clock()
#
# client = gr_api.get_client()
# print close_ver_db(['hello','world'], 5)
# print select_candidate_set_for_book_ver_db(50, 5)
# print recommend_book_ver_db(5, 10)
# print close_ver_db(['fiction'], 13)
# print(resem_ver_db(50, 50))
# id = gr_api.get_auth_user_id(client)
# print "list recommend : %s"% recommend_book(gr_api.get_user_books(id, client), select_candidate_set(id, client), client)
# print "Spending time : %s" % (time.clock() - start)