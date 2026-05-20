import { useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import "./SessionRating.css";

import {
  FaRegFrown,
  FaRegMeh,
  FaRegSmile
} from "react-icons/fa";

export default function SessionRating() {

  const [rating, setRating] = useState(null);
  const [message, setMessage] = useState("");

  const { t } = useLanguage();

  const ratings = [
    {
      value: 1,
      icon: <FaRegFrown />,
      color: "#ef334f"
    },
    {
      value: 2,
      icon: <FaRegFrown />,
      color: "#ff8a1c"
    },
    {
      value: 3,
      icon: <FaRegMeh />,
      color: "#f6cf2f"
    },
    {
      value: 4,
      icon: <FaRegSmile />,
      color: "#a6d90f"
    },
    {
      value: 5,
      icon: <FaRegSmile />,
      color: "#55d05a"
    }
  ];

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

        {ratings.map((item) => (
          <button
            key={item.value}
            type="button"
            className={
              rating === item.value
                ? "face-rating-btn active"
                : "face-rating-btn"
            }
            style={{
              background: item.color
            }}
            onClick={() => {
              setRating(item.value);
              setMessage("");
            }}
          >
            <span className="rating-icon">
              {item.icon}
            </span>
          </button>
        ))}

      </div>

      <div className="rating-bar">

        {ratings.map((item) => (
          <div
            key={item.value}
            className="rating-bar-segment"
            style={{
              background: item.color
            }}
          />
        ))}

      </div>

      {message && (
        <p className="rating-message">
          {message}
        </p>
      )}

    </div>
  );
}