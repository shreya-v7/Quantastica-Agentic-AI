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
    <div className="min-h-screen bg-darkBlue text-white p-4 sm:p-6 md:p-10 space-y-10 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl sm:text-4xl font-bold mb-2">Market News & Analysis</h1>
        <p className="text-gray-400 text-sm sm:text-base max-w-2xl mx-auto">
          Stay updated with the latest financial news and AI-generated analysis tailored to your portfolio.
        </p>
      </div>

      {/* Search */}
      <form
        onSubmit={handleSearch}
        className="max-w-md mx-auto flex items-center gap-2 bg-[#1e2430] p-3 rounded-lg shadow-md"
      >
        <Search className="text-accent h-5 w-5" />
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Search topic..."
          className="flex-1 bg-transparent outline-none text-sm text-white placeholder-gray-500"
        />
        <button
          type="submit"
          className="bg-accentBlue text-white text-sm font-medium px-3 py-1 rounded-lg hover:bg-accentPurple transition"
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
            className="group bg-[#161b22] rounded-xl overflow-hidden shadow-lg hover:shadow-accent transition-all border border-gray-700 transform hover:-translate-y-1 hover:scale-105 duration-300"
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
              <p className="text-gray-400 text-sm mb-4 group-hover:text-white transition-colors">
                {item.description}
              </p>
              <div className="text-xs text-gray-500">{new Date(item.publishedAt).toLocaleString()}</div>
            </div>
          </a>
        ))}
      </div>

      {/* AI Insights */}
      <div className="bg-[#0d1117] p-6 md:p-8 rounded-2xl shadow-xl border border-accentBlue max-w-6xl mx-auto animate-slide-up">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-3 text-accent mb-2 md:mb-0">
            <LineChart className="h-6 w-6 animate-pulse" />
            <h2 className="text-xl font-semibold">AI Insights</h2>
          </div>
          <p className="text-sm text-gray-400 max-w-2xl">
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
        <p className="text-gray-300 text-sm">
          The overall market sentiment is bullish today, driven by positive macroeconomic indicators and strong earnings reports. Sector rotation is visible with increased focus on IT, Pharma, and Banking.
        </p>
      </div>
    </div>
  );
};

export default NewsAnalysisPage;
