// src/NewsPluginComponent.tsx
import React, { useEffect, useState } from "react";
import axios from "axios";

export const NewsPluginComponent = ({ topic }: { topic: string }) => {
  const [news, setNews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHeadlines = async () => {
      try {
        const response = await axios.post(
          "http://34.30.201.70:5001/getHeadlines",
          { topic: topic },
          { headers: { "Content-Type": "application/json" } }
        );
        setNews(response.data);
      } catch (error) {
        console.error("Failed to fetch headlines:", error);
        setNews([]);
      } finally {
        setLoading(false);
      }
    };

    fetchHeadlines();
  }, [topic]);

  if (loading) return <p>Loading news...</p>;

  return (
    <div style={{ color: "white", fontFamily: "Arial", padding: "1rem", backgroundColor: "#1e293b" }}>
      <h3>📰 Top News for <em>{topic}</em></h3>
      {news.length === 0 && <p>No news found for this topic.</p>}
      {news.map((item, i) => (
        <div key={i} style={{ margin: "1rem 0", borderBottom: "1px solid #334155", paddingBottom: "0.5rem" }}>
          <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ color: "#38bdf8", fontWeight: "bold" }}>
            {item.title}
          </a>
          <p style={{ fontSize: "0.9rem", color: "#94a3b8" }}>{item.source} — {new Date(item.publishedAt).toLocaleString()}</p>
          <p>{item.description}</p>
        </div>
      ))}
    </div>
  );
};
