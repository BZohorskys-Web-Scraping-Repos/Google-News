import requests
import sys
import webbrowser
import logging
import textwrap
import os

from lxml import etree
from requests.models import parse_header_links

SITE = 'https://news.google.com'
TOPSTORIES = 'https://news.google.com/topstories'
TAB = '  '
TERMINAL_WIDTH = os.get_terminal_size().columns if os.get_terminal_size().columns < 80 else 80

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s',
)

def main():
    r = requests.get(TOPSTORIES)
    if r.status_code == 200:
        page_html = etree.HTML(r.content)

        # gets category headers and content
        data = page_html.xpath('//main//h2 | //main//div[@jslog and not(@data-n-st) and not(@tabindex)]')
        for element in data:
            if element.tag == 'h2':
                title = ''.join(element.xpath('.//text()'))
                print(title.center(TERMINAL_WIDTH, ' '))
                print('=' * TERMINAL_WIDTH)
            else:
                main_article_link = SITE + ''.join(element.xpath('./div/div/a/@href'))[1:]
                article_header = ''.join(element.xpath('./div/div/article/h3/descendant-or-self::*/text()')).encode('latin1').decode('utf-8')
                publisher = ''.join(element.xpath('./div/div/article/div/div/a/text()'))
                publish_time = ''.join(element.xpath('./div/div/article/div/div/time/text()'))
                print(article_header)
                print(main_article_link)
                print(f'{TAB}{publisher}: {publish_time}')
                print()
                user_response = input("Continue, Open, or Quit? (ENTER/o/q)")
                print()
                if user_response == '':
                    pass
                elif user_response == 'o':
                    webbrowser.open(main_article_link)
                    user_response = input("Continue or Quit? (ENTER/q)")
                    print()
                    if user_response == '':
                        pass
                    else:
                        return 0
                else:
                    return 0
            

        us_news_link = page_html.xpath('//div[@aria-label="U.S."]/a[1]/@href')
        world_news_link = page_html.xpath('//div[@aria-label="World"]/a[1]/@href')
        business_news_link = page_html.xpath('//div[@aria-label="Business"]/a[1]/@href')
        technolog_news_link = page_html.xpath('//div[@aria-label="Technology"]/a[1]/@href')
        entertainment_news_link = page_html.xpath('//div[@aria-label="Entertainment"]/a[1]/@href')
        sports_news_link = page_html.xpath('//div[@aria-label="Sports"]/a[1]/@href')
        science_news_link = page_html.xpath('//div[@aria-label="Science"]/a[1]/@href')
        health_news_link = page_html.xpath('//div[@aria-label="Health"]/a[1]/@href')

        links = [
            us_news_link,
            world_news_link,
            business_news_link,
            technolog_news_link,
            entertainment_news_link,
            sports_news_link,
            science_news_link,
            health_news_link,
        ]

        for link in links:
            valid_link = construct_valid_url(link)
            if(valid_link is not False):
                get_news_articles(valid_link)
            else:
                print('Skipping this url')

    else:
        print(f'Recieved {r.status_code} response code.')


def construct_valid_url(url):
    if len(url) != 1:
        print("Erorr: and error occured while constructing a valid url.")
        print(f'There were {len(url)} urls provided.')
        return False
    
    return SITE + url[0][1:]

def get_news_articles(url):
    r = requests.get(url)
    if r.status_code == 200:
        page_html = etree.HTML(r.content)

        data = page_html.xpath('//body/c-wiz[last()]//div[not(@*)]')[0]
        title = data.xpath('.//h2/text()')[0]
        articles = data.xpath('.//main//main/div/div')

        print(title.center(TERMINAL_WIDTH, ' '))
        print('=' * TERMINAL_WIDTH)

        loop = 0
        for article in articles:
            if loop > 4:
                break
            article_link = SITE + ''.join(article.xpath('.//h3/a/@href'))
            article_header = ''.join(article.xpath('.//h3/a/text()')).encode('latin1').decode('utf-8')
            publishers = article.xpath('.//article/div/div/a/text()')
            publish_times = article.xpath('.//article/div/div/time/text()')
            print(article_header)
            print(article_link)
            print_publishers_and_times(publishers, publish_times)
            loop += 1
            user_response = input("Continue, Open, or Quit? (ENTER/o/q)")
            print()
            if user_response == '':
                pass
            elif user_response == 'o':
                webbrowser.open(article_link)
                user_response = input("Continue or Quit? (ENTER/q)")
                print()
                if user_response == '':
                    pass
                else:
                    return 0
            else:
                return 0

def print_publishers_and_times(publishers, publish_times):
    for idx in range(len(publishers)):
        print(f'{TAB}{publishers[idx]}: {publish_times[idx]}')

if __name__ == '__main__':
    main()
