#! /usr/bin/env python3
# coding:utf-8


# ===============================================

import requests
from bs4 import BeautifulSoup as bs
import csv
import os
import urllib.request

# ===============================================

address_site = "http://books.toscrape.com/"
dossier = "/home/mike/OC_DA_Python/Projet_2/Books_to_Scrape_Images/"

# ===============================================


def title_category():
    """
    Search all category titles
    """

    title_category = []
    r_url = requests.get(address_site + 'catalogue/category/books_1/index.html')
    bs_page = bs(r_url.text, 'html.parser')

    for list_link in bs_page.find('ul', class_='nav-list')('ul')[0]('li'):
        title_category.append(list_link.find('a').text.strip())

    return sorted(title_category)

# ===============================================


def category_link():
    """
     search all categories
    """

    links = []
    r_url = requests.get(address_site + 'catalogue/category/books_1/index.html')
    bs_page = bs(r_url.text, 'html.parser')

    for list_link in bs_page.find_all('ul', class_='nav-list')[0]('ul')[0]('li'):
        links.append(address_site + "catalogue/category/" + list_link('a')[0]['href'][3:])

    return sorted(links)

# ===============================================


def nb_page_by_category(param):
    """
    search the number of pages by category
    """

    list_by_page = []

    for x in param:

        url_page = x[0:-10]
        list_by_page.append(x)

        page = requests.get(x)
        bs_page = bs(page.text, 'html.parser')

        while bs_page.find_all('li', class_='next'):

            url_next_page = url_page + bs_page.find_all('li', class_='next')[0]('a')[0]['href']
            list_by_page.append(url_next_page)

            npage_next = requests.get(url_next_page)
            bs_page = bs(npage_next.text, 'html.parser')

    return list_by_page

# ===============================================


def book_info(param):
    """
    infos by book
    """

    infos_articles = []

    for x in param:

        page = requests.get(x)
        article = bs(page.text, 'html.parser')

        for url_article in article.find_all('div', class_="image_container"):
            product_page_url = address_site + "catalogue" + url_article.find_all('a')[0]['href'][8:]

            info = requests.get(product_page_url)
            page_article = bs(info.text, 'html.parser')

            info_article = []
            for info in page_article.find_all('article', class_="product_page"):
                upc = info.find_all('tr')[0]('td')[0].text
                titre = info.find('h1').text
                price_including_tax = info.find_all('tr')[3]('td')[0].text[1:]
                price_excluding_tax = info.find_all('tr')[2]('td')[0].text[1:]
                number_available = info.find_all('tr')[5]('td')[0].text
                product_description = info.find('h2').find_next('p').text
                url_image = address_site + info.find_all('img')[0]['src'][6:]

            for info in page_article.find_all('ul', class_='breadcrumb'):
                category = info.find_all('li')[2].text.strip()

            for info in page_article.find_all('div', class_='content'):
                review_rating = info.find('p', class_='star-rating')['class'][1]

            info_article.append(product_page_url)
            info_article.append(upc)
            info_article.append(titre)
            info_article.append(price_including_tax)
            info_article.append(price_excluding_tax)
            info_article.append(number_available)
            info_article.append(product_description)
            info_article.append(category)
            info_article.append(review_rating)
            info_article.append(url_image)

            infos_articles.append(info_article)

    return infos_articles

# ===============================================


def create_folders_and_pics_by_category(category):
    """
    Folder creation by category and image downloads
    """

    for x in category:

        page = requests.get(x)
        page_article = bs(page.text, 'html.parser')

        for link in page_article.find_all('div', class_='page-header action'):
            link_category = link('h1')[0].text

            print('\n-----------------------------------------------------------')
            print(f'Downloading of Images and creation of the category folder : {link_category}')
            print('-----------------------------------------------------------\n')

            if os.path.exists(f'{dossier}'):
                pass
                print(f'> The folder exist : {dossier}')

            else:
                os.mkdir(f"{dossier}")
                print(f'> The folder has been created : {dossier}')

            if os.path.exists(f'{dossier}{link_category}'):
                pass
                print(f'> The folder exist : {dossier}{link_category}\n\n')

            else:
                os.mkdir(f"{dossier}{link_category}")
                print(f'> The folder has been created : {dossier}{link_category}\n\n')

            for y in nb_page_by_category([x]):

                page = requests.get(y)
                bs_page = bs(page.text, 'html.parser')

                for z in bs_page.find_all('div', class_='image_container'):
                    image_name = z('a')[0]('img')[0]['src'][-36:]
                    url_image = address_site + z('a')[0]('img')[0]['src'][12:]
                    print(f"\n> Url image : {url_image}")
                    file_path = f"{dossier}{link_category}/{image_name}"
                    print(f"> Path : {file_path}")

                    if os.path.isfile(f"{dossier}{link_category}/{image_name}"):
                        print(f"> The file already has been saved : {image_name}")
                        print('\n')

                    else:
                        urllib.request.urlretrieve(url_image, file_path)
                        print(f"> Image for downloading : {image_name}")
                        print('\n')

# ===============================================


def backup_data(info_book, filename):
    """
    Saves information and books in the selected categories
    """

    with open(f'{filename}.csv', 'w', newline='\n') as f:

        file_csv = csv.writer(f)
        file_csv.writerow(['Product_page_url', 'Upc', 'Titre', 'Price_including_tax',
                           'Price_excluding_tax', 'Number_available', 'Product_description',
                           'Category', 'Review_rating', 'Image_url'])

        for x in info_book:
            file_csv.writerow(x)

# ===============================================


def main():

    while True:

        print(f'\n==============================================================\n\
        \rCategory of website : {address_site}\n\
        \r==============================================================\n')

        for k, v in enumerate(title_category()):
            print(f"N°{k} : {v}")

        print(f'\n+++ Others options ---------------------------------------------\n\
        \rN°{k + 1} : All categories by book (separate image folders)\n\
        \rN°{k + 2} : All categories in one file (separate image folders)\n\
        \rN°{k + 3} : Quit the program\n\
        \r================================================================')


        print('\n--------------------------------------------')
        choice = input(' Select a category or option of [ 0 to 52 ] : ')
        print('--------------------------------------------\n')

        try:
            choice = int(choice)

        except (TypeError, ValueError, NameError):
            continue

        if choice >= 0 and choice <= 49:
            all_pages = nb_page_by_category([category_link()[choice]])
            infos_books = book_info(all_pages)
            backup_data(infos_books, title_category()[choice])
            create_folders_and_pics_by_category([category_link()[choice]])

        elif choice == 50:
            i = 0
            for x in category_link():
                all_pages = nb_page_by_category([x])
                infos_books = book_info(all_pages)
                backup_data(infos_books, title_category()[i])
                create_folders_and_pics_by_category([x])
                i += 1

        elif choice == 51:
            category = category_link()
            all_pages = nb_page_by_category(category)
            infos_books = book_info(all_pages)
            backup_data(infos_books, 'all categories')
            create_folders_and_pics_by_category(category)

        elif choice == 52:
            return False

        else:
            continue

        return False

# ===============================================


if __name__ == "__main__":
    main()
