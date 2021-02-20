#! /usr/bin/env python3
# coding:utf-8


# ===============================================

import csv
import os
import time
import urllib.parse
import urllib.request

import requests
from bs4 import BeautifulSoup as Bs

# ===============================================

ADDRESS_SITE = "http://books.toscrape.com/"
DATAS_FOLDER = f"{os.getcwd()}/Books_to_scrape_datas/"
IMAGES_FOLDER = f"{os.getcwd()}/Books_to_scrape_images/"

# ===============================================


def title_category():
    """
    Search all category titles
    """

    titles = []

    r_url = requests.get(ADDRESS_SITE)
    bs_page = Bs(r_url.content, "html.parser")

    for list_link in bs_page.find("ul", class_="nav-list")("ul")[0]("li"):
        titles.append(list_link.find("a").text.strip())

    return titles


# ===============================================


def category_link():
    """
    search all categories
    """

    links = []
    r_url = requests.get(ADDRESS_SITE)
    bs_page = Bs(r_url.content, "html.parser")

    for list_link in bs_page.find_all("ul", class_="nav-list")[0]("ul")[0]("li"):
        links.append(urllib.parse.urljoin(ADDRESS_SITE, list_link("a")[0]["href"]))

    return links


# ===============================================


def nb_page_by_category(category):
    """
    search the number of pages by category
    """

    list_by_page = []

    for page_by_book in category:

        list_by_page.append(page_by_book)

        url_page = page_by_book.rpartition("index.html")[0]

        page = requests.get(page_by_book)
        bs_page = Bs(page.content, "html.parser")

        while bs_page.find("li", class_="next"):

            url_next_page = urllib.parse.urljoin(
                url_page, bs_page.find_all("li", class_="next")[0]("a")[0]["href"]
            )
            list_by_page.append(url_next_page)

            n_page_next = requests.get(url_next_page)
            bs_page = Bs(n_page_next.content, "html.parser")

    return list_by_page


# ===============================================


def book_info(nb_page_category):
    """
    infos by book
    """
    infos_articles = []

    for urls_page in nb_page_category:

        page = requests.get(urls_page)
        art = Bs(page.content, "html.parser")

        for url_article in art.find_all("div", class_="image_container"):

            info_article = []

            url_split = f"catalogue/{url_article.find_all('a')[0]['href'].rpartition('../')[2].rpartition('index')[0]}"
            product_page_url = urllib.parse.urljoin(ADDRESS_SITE, url_split)

            info = requests.get(product_page_url)
            book = Bs(info.content, "html.parser")

            # product_page_url
            info_article.append(product_page_url)

            # universal_ product_code (upc)
            info_article.append(
                book.find("table", class_="table table-striped")("tr")[0]("td")[
                    0
                ].text.strip()
            )

            # title
            info_article.append(
                book.find("div", class_="col-sm-6 product_main")("h1")[0].text.strip()
            )

            # price_including_tax
            info_article.append(
                book.find("table", class_="table-striped")("tr")[3]("td")[
                    0
                ].text.strip()
            )

            # price_excluding_tax
            info_article.append(
                book.find("table", class_="table-striped")("tr")[2]("td")[
                    0
                ].text.strip()
            )

            # number_available
            info_article.append(
                book.find("p", class_="instock availability").text.strip()
            )

            # product_description
            info_article.append(
                book.find("div", class_="sub-header")("h2")[0]
                .find_next("p")
                .text.strip()
            )

            # category
            info_article.append(
                book.find("ul", class_="breadcrumb")("li")[2].text.strip()
            )

            # review_rating
            info_article.append(
                book.find("p", class_="star-rating")["class"][1].strip()
            )

            # image_url
            img_name_path = (
                book.find("div", class_="item active")("img")[0]["src"]
                .rpartition("../")[2]
                .strip()
            )
            info_article.append(urllib.parse.urljoin(ADDRESS_SITE, img_name_path))

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
        page_article = Bs(page.content, "html.parser")

        link_category = page_article.find("div", class_="page-header action")("h1")[
            0
        ].text.strip()

        print(
            f"\n\n\n\n-----------------------------------------------------------\n\
                \rDownloading of Images and creation of the category folder : {link_category}\n\
                \r-----------------------------------------------------------\n"
        )

        path_image = f"{IMAGES_FOLDER}{link_category}"
        os.makedirs(path_image, exist_ok=True)

        for all_page_by_category in nb_page_by_category([url_category]):

            page = requests.get(all_page_by_category)
            bs_page = Bs(page.content, "html.parser")

            for url_image in bs_page.find_all("div", class_="image_container"):

                img_name = url_image("a")[0]("img")[0]["src"].rpartition("/")[2]
                img_name_path = url_image("a")[0]("img")[0]["src"].rpartition("../")[2]
                img_name_full_path = urllib.parse.urljoin(
                    ADDRESS_SITE, f"{img_name_path}"
                )

                print(f"> Url image : {img_name_full_path}")
                print(f"> Destination : {IMAGES_FOLDER}{link_category}")

                if os.path.isfile(f"{IMAGES_FOLDER}{link_category}/{img_name}"):
                    print(f"> Url image : Already downloaded\n")

                else:
                    urllib.request.urlretrieve(
                        img_name_full_path, f"{IMAGES_FOLDER}{link_category}/{img_name}"
                    )
                    print(
                        f"> Image for downloading : {url_image('a')[0]('img')[0]['src'].rpartition('/')[2]}\n"
                    )


# ===============================================


def backup_data(info_book, filename):
    """
    Saves information and books in the selected categories
    """

    os.makedirs(DATAS_FOLDER, exist_ok=True)

    with open(
        f"{DATAS_FOLDER}{filename}.csv", "w", newline="\n", encoding="utf-8-sig"
    ) as f:

        file_csv = csv.writer(f)
        file_csv.writerow(
            [
                "Product_page_url",
                "Upc",
                "Titre",
                "Price_including_tax",
                "Price_excluding_tax",
                "Number_available",
                "Product_description",
                "Category",
                "Review_rating",
                "Image_url",
            ]
        )

        file_csv.writerows(info_book)

    print(
        f'>>> Downloads of data and images for the category < "{filename}" > are complete\n'
    )


# ===============================================


def main():

    category = category_link()
    title = title_category()

    while True:

        print(
            f"\n==============================================================\n\
                 \rCategory of website : {ADDRESS_SITE}\n\
                 \r==============================================================\n"
        )

        for k, v in enumerate(title_category()):
            print(f"N°{k} : {v}")

        print(
            f"\n+++ Others options ---------------------------------------------\n\
                \rN°50 : All categories by book (separate image folders)\n\
                \rN°51 : All categories in one file (separate image folders)\n\
                \rN°52 : Quit the program\n\
                \r================================================================"
        )

        print("\n---------------------------------------------")
        choice = input(" Select a category or option of [ 0 to 52 ] : ")
        print("---------------------------------------------\n")

        try:
            choice = int(choice)

        except (TypeError, ValueError, NameError):
            print(
                "\n\n******************************************************\n\
                  \r|   Input error, specify a number between 0 and 52   |\n\
                  \r******************************************************\n"
            )
            time.sleep(5)
            continue

        if 0 <= choice <= 49:
            """
            > Choose < 0 - 49 > to retrieve the information from a particular book in a separate file
            > The image folder will be downloaded separately
            """
            all_pages = nb_page_by_category([category[choice]])
            infos_books = book_info(all_pages)
            create_folders_and_pics_by_category([category[choice]])
            backup_data(infos_books, title[choice])

        elif choice == 50:
            """
            > Choose <50> to retrieve all the information in a different file book by book
            > The images will be uploaded in a separate folder.
            > The treatment is done in one go for all categories
            """
            for i, link_category in enumerate(category):
                all_pages = nb_page_by_category([link_category])
                infos_books = book_info(all_pages)
                create_folders_and_pics_by_category([link_category])
                backup_data(infos_books, title[i])

        elif choice == 51:
            """ 
            > Choose <51> to retrieve all the information from the books in a single file
            > The images will be uploaded in a separate folder.
            > The treatment is done in one go for all categories
            """
            all_pages = nb_page_by_category(category)
            infos_books = book_info(all_pages)
            create_folders_and_pics_by_category(category)
            backup_data(infos_books, "all categories")

        elif choice == 52:
            """
            > Quit the script
            """
            break


# ===============================================


if __name__ == "__main__":
    main()
