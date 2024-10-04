import requests
import time
from bs4 import BeautifulSoup
import csv
import os

session = requests.Session()

def fetch_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = session.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.text
        else:
            print(f"Ошибка при доступе к {url}, код: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None
    

def parse_review_page(url, review_index):
    page_content = fetch_page(url)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')

        reviews = soup.find_all('div', class_='review-title')

        for review in reviews:
            name_review = review.find('a').get_text(strip=True)
            href_review = review.find('a')['href']
            full_href = "https://otzovik.com" + href_review

            rating = review.find('span', class_='review-rating').get_text(strip=True)
            review_page_data = parse_single_review(full_href)
            review_data = {
                'NameReview': name_review,
                'Rating': rating,
                'Review': review_page_data.get('Review'),
                'ReviewPlus': review_page_data.get('ReviewPlus'),
                'ReviewMinus': review_page_data.get('ReviewMinus'),
                'PostDate': review_page_data.get('PostDate')
            }

            filename = f"sberbank_reviews_{review_index:04d}.csv"
            save_single_review_to_csv(review_data, filename)

            review_index += 1

            time.sleep(2)

        return review_index
    return review_index


def parse_single_review(url):
    page_content = fetch_page(url)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')

        review_plus = soup.find('div', class_='review-plus')
        review_minus = soup.find('div', class_='review-minus')
        review_body = soup.find('div', class_='review-body', itemprop='description')
        post_date = soup.find('abbr', class_='value')

        return {
            'ReviewPlus': review_plus.get_text(strip=True) if review_plus else '',
            'ReviewMinus': review_minus.get_text(strip=True) if review_minus else '',
            'Review': review_body.get_text(strip=True) if review_body else '',
            'PostDate': post_date['title'] if post_date else ''
        }
    return {}


def save_single_review_to_csv(review_data, filename):
    is_new_file = not os.path.exists(filename)

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['NameReview', 'Rating', 'Review', 'ReviewPlus', 'ReviewMinus', 'PostDate']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

        if is_new_file:
            writer.writeheader()  

        writer.writerow(review_data) 

start_page_url = "https://otzovik.com/reviews/sberbank_rossii/"
review_index = 1 

review_index = parse_review_page(start_page_url, review_index)