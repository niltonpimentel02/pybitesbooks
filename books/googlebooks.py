import requests
from urllib import parse

from .models import Category, Book, Search

BASE_URL = "https://www.googleapis.com/books/v1/volumes"
SEARCH_URL = BASE_URL + "?q={}"
BOOK_URL = BASE_URL + "/{}"
NOT_FOUND = "Not found"
DEFAULT_LANGUAGE = "en"


def get_book_info(book_id):
    """cache book info in db"""
    book = get_book_info_from_cache(book_id)
    if book is not None:
        return book
    return get_book_info_from_api(book_id)


def get_book_info_from_cache(book_id):
    books = Book.objects.filter(bookid=book_id)
    return books[0] if books else None


def get_book_info_from_api(book_id):
    query = BOOK_URL.format(book_id)
    resp = requests.get(query).json()

    volinfo = resp["volumeInfo"]

    bookid = book_id
    title = volinfo["title"]
    authors = ", ".join(volinfo.get("authors", NOT_FOUND))
    publisher = volinfo.get("publisher", NOT_FOUND).strip('"')
    published = volinfo.get("publishedDate", NOT_FOUND)

    identifiers = volinfo.get("industryIdentifiers")
    isbn = identifiers[-1]["identifier"] if identifiers else NOT_FOUND

    pages = volinfo.get("pageCount", 0)
    language = volinfo.get("language", DEFAULT_LANGUAGE)
    description = volinfo.get("description", "No description")

    categories = volinfo.get("categories", [])
    category_objects = []
    for category in categories:
        cat, _ = Category.objects.get_or_create(name=category)
        category_objects.append(cat)

    if "imageLinks" in volinfo and "small" in volinfo["imageLinks"]:
        image_size = parse.parse_qs(
            parse.urlparse(volinfo["imageLinks"]["small"]).query
        )["zoom"][0]
    else:
        image_size = "1"

    book, created = Book.objects.get_or_create(bookid=bookid)

    # make sure we don't created duplicates
    if created:
        book.title = title
        book.authors = authors
        book.publisher = publisher
        book.published = published
        book.isbn = isbn
        book.pages = pages
        book.language = language
        book.description = description
        book.imagesize = image_size
        book.save()

    # if no categories yet add them
    if category_objects and book.categories.count() == 0:
        book.categories.add(*category_objects)
        book.save()

    return book


def search_books(term, request=None, lang=None):
    """autocomplete = keep this one api live / no cache"""
    search = Search(term=term)
    if request and request.user.is_authenticated:
        search.user = request.user
    search.save()

    query = SEARCH_URL.format(term)

    if lang is not None:
        query += f"&langRestrict={lang}"

    return requests.get(query).json()


if __name__ == "__main__":
    term = "python for finance"
    for item in search_books(term)["items"]:
        try:
            id_ = item["id"]
            title = item["volumeInfo"]["title"]
        except KeyError:
            continue
        print(id_, title)
