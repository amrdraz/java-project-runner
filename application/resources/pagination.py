"""
Pagination helpers.
"""
import itertools
import math

def paginate_iterable(iterable, page, per_page):
    """
    Pagination for custom iterables.
    returns an iterator.
    """
    start = (page -1) * per_page
    end = start + per_page
    return itertools.islice(iterable, start, end)


def mongo_paginate_to_dict(pages, items_key, convert_items=True, **nestedkwargs):
    """
    Converts a page from mongoengine paginate to a dict for marshalling.
    optionally converts items to dict.
    """
    dic = {
       'page': pages.page,
       'pages': pages.pages
    }
    if convert_items:
        dic[items_key] = [item.to_dict(**nestedkwargs) for item in pages.items()]
    else:
        dic[items_key] = pages.items()
    return dic

def custom_paginate_to_dict(iterable, items_key, page, total ,per_page, convert_items, **nestedkwargs):
    """
    Converts a page from paginate_iterable to a dict for marshalling.
    optionally converts items to dict.
    """
    pages = int(math.ceil(total / float(per_page)))
    if convert_items:
        items = [item.to_dict(**nestedkwargs) for item in iterable]
    else:
        items = list(iterable)
    dic = {
        "page": page,
        "pages": pages,
    }
    dic[items_key] = items
    return dic
