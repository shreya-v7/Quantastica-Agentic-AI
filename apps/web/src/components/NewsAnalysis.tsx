import React, { useEffect, useState } from "react";
import axios from "axios";
import { Newspaper, TrendingUp, LineChart, Search } from "lucide-react";

interface NewsItem {
  title: string;
  source: string;
  description: string;
  publishedAt: string;
  url: string;
  urlToImage: string;
}

const NewsAnalysisPage: React.FC = () => {
  const [newsData, setNewsData] = useState<NewsItem[]>([]);
  const [topic, setTopic] = useState<string>("finance");

  const fetchNews = async (query: string) => {
    try {
      const response = await axios.post(
        "http://localhost:5000/getHeadlines",
        { topic: query },
        { headers: { "Content-Type": "application/json" } }
      );
      // Set array of articles
      setNewsData(response.data || []);
    } catch (error) {
      console.error("Error fetching news:", error);
    }
  };

  useEffect(() => {
    fetchNews(topic);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchNews(topic);
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-4 sm:p-6 md:p-10 space-y-10 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl sm:text-4xl font-bold mb-2">Market News & Analysis</h1>
        <p className="text-muted-foreground text-sm sm:text-base max-w-2xl mx-auto">
          Stay updated with the latest financial news and AI-generated analysis tailored to your portfolio.
        </p>
      </div>

      {/* Search */}
      <form
        onSubmit={handleSearch}
        className="mx-auto flex max-w-md items-center gap-2 rounded-xl border border-border bg-card p-3 shadow-sm dark:bg-card"
      >
        <Search className="h-5 w-5 shrink-0 text-primary" aria-hidden />
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Search topic..."
          className="min-w-0 flex-1 bg-transparent py-2 text-sm text-foreground outline-none placeholder:text-muted-foreground"
        />
        <button
          type="submit"
          className="bg-primary text-primary-foreground text-sm font-medium px-3 py-1 rounded-lg hover:opacity-90 transition"
        >
          Search
        </button>
      </form>

      {/* News Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {newsData.map((item, index) => (
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            key={index}
            className="group bg-card rounded-xl overflow-hidden shadow-lg hover:shadow-accent transition-all border border-border transform hover:-translate-y-1 hover:scale-105 duration-300"
          >
            {item.urlToImage && (
              <img
                src={item.urlToImage}
                alt="News"
                className="w-full h-48 object-cover group-hover:opacity-80 transition-opacity"
              />
            )}
            <div className="p-4 flex flex-col justify-between">
              <div className="flex items-center gap-2 text-accent mb-2">
                <Newspaper className="h-5 w-5 group-hover:rotate-6 transition-transform" />
                <span className="text-sm font-medium">{item.source}</span>
              </div>
              <h3 className="text-lg font-semibold mb-2 group-hover:text-accent transition-colors">
                {item.title}
              </h3>
              <p className="text-muted-foreground text-sm mb-4 group-hover:text-foreground transition-colors">
                {item.description}
              </p>
              <div className="text-xs text-muted-foreground">{new Date(item.publishedAt).toLocaleString()}</div>
            </div>
          </a>
        ))}
      </div>

      {/* AI Insights */}
      <div className="mx-auto max-w-6xl rounded-2xl border border-primary/25 bg-muted/60 p-6 shadow-xl dark:bg-muted md:p-8 animate-slide-up">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-3 text-accent mb-2 md:mb-0">
            <LineChart className="h-6 w-6 animate-pulse" />
            <h2 className="text-xl font-semibold">AI Insights</h2>
          </div>
          <p className="text-sm text-muted-foreground max-w-2xl">
            Based on today's market trend, tech stocks are expected to outperform in the short term. Keep an eye on IT and FinTech sectors.
          </p>
        </div>
      </div>

      {/* Market Summary */}
      <div className="bg-gradient-to-r from-accentBlue/30 to-accentPurple/20 p-6 md:p-8 rounded-2xl shadow-lg max-w-6xl mx-auto space-y-4">
        <div className="flex items-center gap-3 text-accent">
          <TrendingUp className="h-5 w-5" />
          <h3 className="text-lg font-semibold">Overall Market Summary</h3>
        </div>
        <p className="text-card-foreground text-sm">
          The overall market sentiment is bullish today, driven by positive macroeconomic indicators and strong earnings reports. Sector rotation is visible with increased focus on IT, Pharma, and Banking.
        </p>
      </div>
    </div>
  );
};

export default NewsAnalysisPage;
