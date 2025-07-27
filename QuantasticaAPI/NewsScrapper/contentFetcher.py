import requests
from bs4 import BeautifulSoup
from newspaper import Article
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='5a8e53cb70034f2795efb5317c39d42b')

def fetch_clean_content(url):
    """Extract clean article content instead of raw HTML"""
    try:
        # Method 1: Try newspaper3k first (best for news articles)
        article = Article(url)
        article.download()
        article.parse()

        if article.text and len(article.text) > 100:
            print(f"✅ Extracted using newspaper3k")
            print(f"📰 Title: {article.title}")
            print(f"📊 Content Length: {len(article.text)} characters")
            print(f"👥 Authors: {article.authors}")
            print(f"📅 Publish Date: {article.publish_date}")
            print(f"\n📖 Clean Content:")
            print("-" * 50)
            return article.text
        else:
            raise Exception("newspaper3k failed, trying BeautifulSoup")

    except Exception as e:
        # Method 2: Fallback to BeautifulSoup
        print(f"⚠️ newspaper3k failed: {e}")
        print("🔄 Trying BeautifulSoup method...")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()

        # Extract all paragraphs
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

        print(f"✅ Extracted using BeautifulSoup")
        print(f"📊 Content Length: {len(content)} characters")
        print(f"\n📖 Clean Content:")
        print("-" * 50)
        return content

# topic = 'Jane Street'
# url = 'https://www.aljazeera.com/economy/2025/7/18/indias-ban-on-jane-street-raises-concerns-over-regulator-role'

# clean_content = fetch_clean_content(url)
# print(clean_content[:1000] + "...")
# topic = input("Enter the topic you want to search for: ")

def getContent(topic):
    res = newsapi.get_everything(q=topic)
    output = []
    for article in res['articles'][:5]:
        print(article)
        content = fetch_clean_content(article['url'])
        output.append({
            "title": article['title'],
            "url": article['url'],
            "content": content
        })
    return output

def getHeadline(topic):
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