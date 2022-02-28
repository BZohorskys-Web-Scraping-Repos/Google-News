import itertools
import aiohttp
import asyncio
import curses
import logging
import os
import requests
import sys
import textwrap
import webbrowser

from lxml import etree
from requests.models import parse_header_links

SITE = 'https://news.google.com'
TOPSTORIES = 'https://news.google.com/topstories'
TAB = '  '
MAX_ARTICLES = 5
TERMINAL_WIDTH = os.get_terminal_size().columns if os.get_terminal_size().columns < 80 else 80

logging.basicConfig(
    level=logging.FATAL,
    format='%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s',
)

async def get_webpage(url):
    logging.debug(locals())
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            code = response.status
            html = await response.text()
            return {'code':code,'html':html}

async def idleAnimation(task):
    logging.debug(locals())
    for frame in itertools.cycle(r'-\|/-\|/'):
        if task.done():
            print('\r', '', sep='', end='', flush=True)
            break
        print('\r', frame, sep='', end='', flush=True)
        await asyncio.sleep(0.2)

def interactive_console(screen, data):
    logging.debug(locals())
    pos = 0
    while pos < len(data):
        screen.clear()
        screen.addstr("({0}/{1})\n".format(pos+1, len(data)))
        for key in data[pos]:
            if not (key == 'link' or key == 'publicationTimes' or data[pos][key] is None):
                if key == 'publishers':
                    if isinstance(data[pos][key], list):
                        for idx, publisher in enumerate(data[pos][key]):
                            screen.addstr(TAB + publisher + ': ' + data[pos]['publicationTimes'][idx] + '\n')
                    else:
                        screen.addstr(TAB + data[pos]['publishers'] + ': ' + data[pos]['publicationTimes'] + '\n')
                else:
                    screen.addstr(data[pos][key] + '\n')
        screen.addstr("Next, Previous, Open, or Quit? (j, k, o, q)")
        user_response = screen.getkey()
        valid_response = False
        while not valid_response:
            if user_response== 'j':
                valid_response = True
                pos += 1
            elif user_response == 'k':
                if pos != 0:
                    valid_response = True
                    pos -= 1
                else:
                    user_response = screen.getkey()
            elif user_response == 'o':
                webbrowser.open(data[pos]['link'])
                user_response = screen.getkey()
            elif user_response == 'q':
                valid_response = True
                pos = len(data)
            else:
                user_response = screen.getkey()

async def main():
    logging.debug(locals())
    webRequestTask = asyncio.create_task(get_webpage(TOPSTORIES))
    await idleAnimation(webRequestTask)
    if webRequestTask.result()['code'] == 200:
        page_html = etree.HTML(webRequestTask.result()['html'])

        linkDict = {
            'world': page_html.xpath('//div[@aria-label="World"]/a[1]/@href'),
            'us': page_html.xpath('//div[@aria-label="U.S."]/a[1]/@href'),
            'business': page_html.xpath('//div[@aria-label="Business"]/a[1]/@href'),
            'technolog': page_html.xpath('//div[@aria-label="Technology"]/a[1]/@href'),
            'entertainment': page_html.xpath('//div[@aria-label="Entertainment"]/a[1]/@href'),
            'sports': page_html.xpath('//div[@aria-label="Sports"]/a[1]/@href'),
            'science': page_html.xpath('//div[@aria-label="Science"]/a[1]/@href'),
            'health': page_html.xpath('//div[@aria-label="Health"]/a[1]/@href'),
        }

        urlTasks = []
        for key in linkDict:
            valid_link = construct_valid_url(linkDict[key])
            if(valid_link is not False):
                urlTasks.append(asyncio.create_task(get_news_articles(valid_link)))
            await idleAnimation(asyncio.gather(*urlTasks))
        dicts = []
        dicts.extend(get_headlines(page_html))
        for task in urlTasks:
            if task.result() is not None:
                dicts.extend(task.result())
        curses.wrapper(interactive_console, dicts)
    else:
        print(f'Received {webRequestTask.result()["code"]} response code.')

def construct_valid_url(url):
    logging.debug(locals())
    if len(url) != 1:
        print("Erorr: and error occured while constructing a valid url.")
        print(f'There were {len(url)} urls provided.')
        return False
    return SITE + url[0][1:]

async def get_news_articles(url):
    logging.debug(locals())
    code = None
    html = None
    articleDicts = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            code = response.status
            html = await response.text()
    if code is not None and html is not None:
        page_html = etree.HTML(html)
        data = page_html.xpath('//body')[0]

        category = data.xpath('.//h2/text()')[0]
        categoryArticles = data.xpath('.//main//main/div/div')

        loop = 0
        for article in categoryArticles:
            if loop > MAX_ARTICLES:
                break
            articleDict = {
                'category': category,
                'header': None,
                'link': None,
                'publicationTimes': None,
                'publishers': None
            }
            articleDict['link'] = SITE + ''.join(article.xpath('.//h3/a/@href'))
            articleDict['header'] = ''.join(article.xpath('.//h3/a/text()'))
            articleDict['publishers'] = article.xpath('.//article/div/div/a/text()')
            articleDict['publicationTimes'] = article.xpath('.//article/div/div/time/text()')
            articleDicts.append(articleDict)
            loop += 1
    return articleDicts

def get_headlines(html):
    logging.debug(locals())
    data = html.xpath('//main//h2 | //main//div[@jslog and not(@data-n-st) and not(@tabindex)]')
    headlines = []
    for element in data:
        if element.tag == 'h2':
            pass
        else:
            articleDict = {
                'category': 'Headline',
                'header': None,
                'link': None,
                'publicationTimes': None,
                'publishers': None
            }
            articleDict['link'] = SITE + ''.join(element.xpath('./div/div/a/@href'))[1:]
            articleDict['header'] = ''.join(element.xpath('./div/div/article/h3/descendant-or-self::*/text()'))
            articleDict['publishers'] = ''.join(element.xpath('./div/div/article/div/div/a/text()'))
            articleDict['publicationTimes'] = ''.join(element.xpath('./div/div/article/div/div/time/text()'))
            headlines.append(articleDict)
    return headlines