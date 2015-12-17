from django.http import HttpResponse
import json
import urllib
from EcommerceAPI.models import Book

__author__ = 'Duy'


def return_response(data, status):
    data_json = json.dumps(data)
    return HttpResponse(data_json, content_type='application/json', status=status)


def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix


def download_photo():
    no_photo = "http://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png"
    path = "D:\PTIT Final\Source\BookEcommerceServer\EcommerceAPI\scripts\images"
    relative_path = "/images"
    count = 0
    list_book = Book.objects.all()
    for book in list_book:
        if book.id < 362:
            continue
        _lst = book.cover_url.split('.')
        extension = _lst[len(_lst) - 1]
        if book.cover_url is not None and book.cover_url != no_photo:
            file_name = "%d_%s.%s"%(book.id, book.isbn, extension)
        elif book.cover_url == no_photo:
            file_name = "no_photo.png"
        file_path = "%s/%s" % (path, file_name)
        downloaded_image = file(file_path, "wb")
        image_on_web = urllib.urlopen(book.cover_url)
        if book.cover_url is not None and book.cover_url != no_photo:
            while True:
                buf = image_on_web.read(65536)
                if len(buf) == 0:
                    break
                downloaded_image.write(buf)
        downloaded_image.close()
        image_on_web.close()
        book.cover_url = "%s/%s"%(relative_path, file_name)
        book.save()
