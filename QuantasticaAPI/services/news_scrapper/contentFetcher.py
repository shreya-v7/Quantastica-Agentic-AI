import os
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key=os.getenv('NEWSAPI_KEY', ''))


def fetch_clean_content(url):
    """Extract clean article content instead of raw HTML."""
    try:
        # Method 1: newspaper3k (best for news articles)
        article = Article(url)
        article.download()
        article.parse()

        if article.text and len(article.text) > 100:
            print(f"[OK] Extracted via newspaper3k -- Title: {article.title}, Length: {len(article.text)} chars")
            return article.text
        else:
            raise Exception("newspaper3k returned insufficient content")

    except Exception as e:
        # Method 2: Fallback to BeautifulSoup
        print(f"[WARN] newspaper3k failed: {e} -- falling back to BeautifulSoup")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()

        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

        print(f"[OK] Extracted via BeautifulSoup -- Length: {len(content)} chars")
        return content


def getContent(topic):
    """Fetch full article content for a topic."""
    res = newsapi.get_everything(q=topic)
    output = []
    for article in res['articles'][:5]:
        content = fetch_clean_content(article['url'])
        output.append({
            "title": article['title'],
            "url": article['url'],
            "content": content,
        })
    return output


def getHeadline(topic):
    """Fetch headlines for a topic (deduplicated, max 5)."""
    res = newsapi.get_everything(q=topic)
    output = []
    seen_urls = set()
    for article in res['articles'][:20]:
        if len(output) >= 5:
            break
        if article['url'] in seen_urls:
            continue

        seen_urls.add(article['url'])
        output.append({
            "url": article['url'],
            "urlToImage": article['urlToImage'],
            "publishedAt": article['publishedAt'],
            "source": article['source']['name'],
            "title": article['title'],
            "description": article['description'],
        })
    return output
