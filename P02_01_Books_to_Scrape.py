#! /usr/bin/env python3
# coding:utf-8


# ===============================================

import csv
import os
import urllib.parse
import urllib.request
import time

import requests
from bs4 import BeautifulSoup as bs

# ===============================================

ADDRESS_SITE = "http://books.toscrape.com/"
DATAS_FOLDER = f"{os.getcwd()}/Books_to_scrape_datas/"
IMAGES_FOLDER = f"{os.getcwd()}/Books_to_Scrape_images/"

# ===============================================


def title_category():
    """
    Search all category titles
    """

    title_category = []

    r_url = requests.get(ADDRESS_SITE)
    bs_page = bs(r_url.text, 'html.parser')

    for list_link in bs_page.find('ul', class_='nav-list')('ul')[0]('li'):
        title_category.append(list_link.find('a').text.strip())

    return title_category

# ===============================================


def category_link():
    """
     search all categories
    """

    links = []
    r_url = requests.get(ADDRESS_SITE)
    bs_page = bs(r_url.text, 'html.parser')

    for list_link in bs_page.find_all('ul', class_='nav-list')[0]('ul')[0]('li'):
        links.append(urllib.parse.urljoin(ADDRESS_SITE, list_link('a')[0]['href']))

    return links

# ===============================================


def nb_page_by_category(category_link):
    """
    search the number of pages by category
    """

    list_by_page = []

    for page_by_book in category_link:

        list_by_page.append(page_by_book)

        url_page = page_by_book.rpartition('index.html')[0]

        page = requests.get(page_by_book)
        bs_page = bs(page.text, 'html.parser')

        while bs_page.find('li', class_='next'):

            url_next_page = urllib.parse.urljoin(url_page, bs_page.find_all('li', class_='next')[0]('a')[0]['href'])
            list_by_page.append(url_next_page)

            n_page_next = requests.get(url_next_page)
            bs_page = bs(n_page_next.text, 'html.parser')

    return list_by_page

# ===============================================


def book_info(nb_page_category):
    """
    infos by book
    """
    infos_articles = []

    for urls_page in nb_page_category:

        page = requests.get(urls_page)
        art = bs(page.text, 'html.parser')

        for url_article in art.find_all('div', class_="image_container"):

            info_article = []

            url_split = f"catalogue/{url_article.find_all('a')[0]['href'].rpartition('../')[2].rpartition('index.html')[0]}"
            product_page_url = urllib.parse.urljoin(ADDRESS_SITE, url_split)

            info = requests.get(product_page_url)
            book = bs(info.text, 'html.parser')

            info_article.append(product_page_url)  # product_page_url
            info_article.append(book.find('table', class_='table table-striped')('tr')[0]('td')[0].text.strip())  # universal_ product_code (upc)
            info_article.append(book.find('div', class_="page-header action"))  # title
            info_article.append(book.find('table', class_='table-striped')('tr')[3]('td')[0].text[1:].strip())  # price_including_tax
            info_article.append(book.find('table', class_='table-striped')('tr')[2]('td')[0].text[1:].strip())  # price_excluding_tax
            info_article.append(book.find('p', class_="instock availability").text.strip())  # number_available
            info_article.append(book.find('div', class_="sub-header")('h2')[0].find_next('p').text.strip())  # product_description
            info_article.append(book.find('ul', class_="breadcrumb")('li')[2].text.strip())  # category
            info_article.append(book.find('p', class_="star-rating")['class'][1].strip())  # review_rating
            info_article.append(urllib.parse.urljoin(ADDRESS_SITE, book.find('div', class_="item active")('img')[0]['src'].rpartition('../')[2]).strip())  # image_url

            infos_articles.append(info_article)

    return infos_articles

# ===============================================


def create_folders_and_pics_by_category(category):
    """
    Folder creation by category and image downloads
    """

    os.makedirs(IMAGES_FOLDER, exist_ok=True)

    for url_category in category:

        page = requests.get(url_category)
        page_article = bs(page.text, 'html.parser')

        link_category = page_article.find('div', class_='page-header action')('h1')[0].text.strip()

        print(f"\n\n\n\n-----------------------------------------------------------\n\
        \rDownloading of Images and creation of the category folder : {link_category}\n\
        \r-----------------------------------------------------------\n")

        path_image = f'{IMAGES_FOLDER}{link_category}'
        os.makedirs(path_image, exist_ok=True)

        for all_page_by_category in nb_page_by_category([url_category]):

            page = requests.get(all_page_by_category)
            bs_page = bs(page.text, 'html.parser')

            for url_image in bs_page.find_all('div', class_='image_container'):

                print(f"> Url image   : {urllib.parse.urljoin(ADDRESS_SITE, url_image('a')[0]('img')[0]['src'].rpartition('../')[2])}")
                print(f"> Destination : {IMAGES_FOLDER}{link_category}/{url_image('a')[0]('img')[0]['src'].rpartition('/')[2]}")

                if os.path.isfile(f"{IMAGES_FOLDER}{link_category}/{url_image('a')[0]('img')[0]['src'].rpartition('/')[2]}"):
                    print(f"> Url image   : Already downloaded\n")

                else:
                    urllib.request.urlretrieve(urllib.parse.urljoin(ADDRESS_SITE, url_image('a')[0]('img')[0]['src'].rpartition('../')[2]), f"{IMAGES_FOLDER}{link_category}/{url_image('a')[0]('img')[0]['src'].rpartition('/')[2]}")
                    print(f"> Image for downloading : {url_image('a')[0]('img')[0]['src'].rpartition('/')[2]}\n")

# ===============================================


def backup_data(info_book, filename):
    """
    Saves information and books in the selected categories
    """

    os.makedirs(DATAS_FOLDER, exist_ok=True)

    with open(f'{DATAS_FOLDER}{filename}.csv', 'w', newline='\n') as f:

        file_csv = csv.writer(f)
        file_csv.writerow(['Product_page_url', 'Upc', 'Titre', 'Price_including_tax',
                           'Price_excluding_tax', 'Number_available', 'Product_description',
                           'Category', 'Review_rating', 'Image_url'])

        for ligne in info_book:
            file_csv.writerow(ligne)

    print(f'>>> Downloads of data and images for the category < "{filename}" > are complete\n')

# ===============================================


def main():

    while True:

        print(f'\n==============================================================\n\
        \rCategory of website : {ADDRESS_SITE}\n\
        \r==============================================================\n')

        for k, v in enumerate(title_category()):
            print(f"N°{k} : {v}")

        print(f'\n+++ Others options ---------------------------------------------\n\
        \rN°50 : All categories by book (separate image folders)\n\
        \rN°51 : All categories in one file (separate image folders)\n\
        \rN°52 : Quit the program\n\
        \r================================================================')

        print('\n---------------------------------------------')
        choice = input(' Select a category or option of [ 0 to 52 ] : ')
        print('---------------------------------------------\n')

        try:
            choice = int(choice)

        except (TypeError, ValueError, NameError):
            print("\n\n******************************************************\n\
                  \r|   Input error, specify a number between 0 and 52   |\n\
                \r******************************************************\n")
            time.sleep(5)
            continue

        if choice >= 0 and choice <= 49:
            all_pages = nb_page_by_category([category_link()[choice]])
            infos_books = book_info(all_pages)
            create_folders_and_pics_by_category([category_link()[choice]])
            backup_data(infos_books, title_category()[choice])
            break

        elif choice == 50:
            for i, category in enumerate(category_link()):
                all_pages = nb_page_by_category([category_link()[i]])
                infos_books = book_info(all_pages)
                create_folders_and_pics_by_category([category_link()[i]])
                backup_data(infos_books, title_category()[i])


        elif choice == 51:
            all_pages = nb_page_by_category(category_link())
            infos_books = book_info(all_pages)
            create_folders_and_pics_by_category(category_link())
            backup_data(infos_books, 'all categories')
            

        elif choice == 52:
            break

        else:
            continue

# ===============================================


if __name__ == "__main__":
    main()
