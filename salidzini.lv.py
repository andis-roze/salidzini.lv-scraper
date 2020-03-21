#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
from lxml import html


def get_shops(url, selector):
    """
    """
    doc = requests.get(url)
    tree = html.fromstring(doc.content)
    return [s.lower() for s in tree.xpath(selector)]


shops = get_shops(
    "https://www.kurpirkt.lv/veikali.php",
    "//ul[@class=\"veikali\"]/li[@class=\"veikals\"]/a/text()"
)


def get_comment_pages(url_tpl, shop, selector):
    """
    """
    page = 0

    while page == 0 or len(comment_page) > 0:
        page += 1
        doc = requests.get(url_tpl.format(shop, page))
        tree = html.fromstring(doc.content)
        comment_page = tree.xpath(selector)

        yield comment_page


def get_rating(comment):
    """
    """
    return comment.xpath(
        ".//div[@itemprop=\"reviewRating\"]/meta[@itemprop=\"ratingValue\"]"
    )[0].attrib.get("content")


def get_rating_date(comment):
    """
    """
    return comment.xpath(
        ".//div[@itemprop=\"datePublished\"]"
    )[0].attrib.get("content")


def get_rating_body(comment):
    """
    """
    ret = comment.xpath(".//div[@itemprop=\"reviewBody\"]/text()")
    return ret[0] if isinstance(ret, list) else ret


data = []
counter = 0
for shop in shops:
    counter += 1
    for comment_page in get_comment_pages(
        "https://www.salidzini.lv/veikals/{}?p={}", 
        shop, 
        "//table[@class=\"comment_table\"]"
    ):
        for comment in comment_page:
            data.append([
                shop,
                get_rating_date(comment),
                get_rating(comment),
                get_rating_body(comment),
            ])
    if counter > 6:
        break
    print(counter, shop)
    
df = pd.DataFrame(data, columns=["Shop", "Date", "Rating", "Comment"])
with pd.ExcelWriter("ratings.xlsx") as writer:
    df.to_excel(writer)

