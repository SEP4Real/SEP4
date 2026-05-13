import { useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import "./SessionRating.css";

export default function SessionRating() {
  const [rating, setRating] = useState(null);
  const [message, setMessage] = useState("");

  const { t } = useLanguage();

  function handleSubmit() {
    if (!rating) {
      setMessage(t.selectRating);
      return;
    }

    localStorage.setItem("sessionRating", rating);
    setMessage(t.ratingSaved);
  }

  return (
    <div className="session-rating-card">
      <h2>{t.sessionRatingTitle}</h2>

      <div className="rating-buttons">
        {[1, 2, 3, 4, 5].map((number) => (
          <button
            key={number}
            type="button"
            className={rating === number ? "rating-button active" : "rating-button"}
            onClick={() => {
              setRating(number);
              setMessage("");
            }}
          >
            {number}
          </button>
        ))}
      </div>

      <button type="button" className="rating-submit" onClick={handleSubmit}>
        {t.submitRating}
      </button>

      {message && <p className="rating-message">{message}</p>}
    </div>
  );
}