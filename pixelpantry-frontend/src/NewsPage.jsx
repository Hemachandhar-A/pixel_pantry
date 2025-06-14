import { useState, useEffect } from "react";
import "./NewsPage.css"; // Optional styling

function NewsPage() {
  const [news, setNews] = useState([]);

  useEffect(() => {
    fetch("/news")
      .then((response) => response.json())
      .then((data) => setNews(data))
      .catch((error) => console.error("Error fetching news:", error));
  }, []);

  return (
    <div className="news-page">
      <h2>Latest Pest & Disease News</h2>
      {news.length > 0 ? (
        <ul className="news-list">
          {news.map((item, index) => (
            <li key={index} className="news-item">
              <a href={item.link} target="_blank" rel="noopener noreferrer">
                {item.headline}
              </a>
            </li>
          ))}
        </ul>
      ) : (
        <p>Loading news...</p>
      )}
    </div>
  );
}

export default NewsPage;
