import multiprocessing
from multiprocessing import Pool

import requests
import re
import time
import uuid
from datetime import datetime
from bs4 import BeautifulSoup
import newspaper
import configparser
import urllib3

headers = {
    'pragma': "no-cache",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en,zh-CN,zh;q=0.8",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'cache-control': "no-cache",
    'connection': "keep-alive",
    'Referer': "http://www.baidu.com",
}


def captureNews(baiduUrl, articleresults):
    try:
        r = requests.get(baiduUrl, timeout=20, headers=headers)
    except requests.exceptions.ConnectionError:
        return ""
    except requests.exceptions.ReadTimeout:
        return ""

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'lxml')
        for one in soup.find_all(attrs={'class': 'result'}):
            title = (one.select('a')[0].get_text()).replace("\n", "").strip()
            webpageUrl = (one.select('a')[0].attrs['href']).replace("\n", "").strip()

            authorSec = one.find_all("p", attrs={'class': 'c-author'})
            authorPre = authorSec[0].get_text().replace("\n", "").replace("\t", "").replace(" ", "")
            try:
                published = ""
                resourse = ""
                author = "".join(authorPre.split())
                res1 = re.search('(\d{4})年(\d{2})月(\d{2})日(\d{2}):(\d{2})', author)
                res2 = re.search('(\d{1,2})小时前', author)
                res3 = re.search('(\d{1,2})分钟前', author)
                if res1:
                    published = res1.group(1) + '-' + res1.group(2) + '-' + res1.group(3) + 'T' + res1.group(
                        4) + ':' + res1.group(5) + ':00Z'
                    resourse = author.replace(res1.group(), '').strip()
                    timeArray = time.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
                    timestamp = time.mktime(timeArray)
                    ttemp = time.localtime(timestamp - 8 * 60 * 60)
                    published = time.strftime("%Y-%m-%dT%H:%M:%SZ", ttemp)
                elif res2:
                    t = time.time() - int(res2.group(1)) * 60 * 60 - 8 * 60 * 60
                    published = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(t))
                    resourse = author.replace(res2.group(), '').strip()
                elif res3:
                    t = time.time() - int(res3.group(1)) * 60 - 8 * 60 * 60
                    published = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(t))
                    resourse = author.replace(res3.group(), '').strip()
                if not resourse:
                    resourse = '百度新闻'
                if not published:
                    published = str(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))

                article = newspaper.Article(webpageUrl, language='zh', headers=headers)
                article.download()
                article.parse()

                if article.text == "":
                    continue
                captureTime = str(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
                data = {"content": article.text,
                        "resourse": resourse,
                        "title": title,
                        "webpageUrl": webpageUrl,
                        "fromType": "7",
                        "captureTime": captureTime,
                        "published": published}
                print(data["title"])
                articleresults.append(data)
            except newspaper.article.ArticleException:
                continue
            except IndexError:
                continue
            except urllib3.exceptions.ReadTimeoutError:
                continue
            except RuntimeError:
                continue
            except urllib3.exceptions.InvalidHeader:
                continue
            except TypeError:
                continue
            except ValueError:
                continue
    else:
        pass

    return articleresults
