import { useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import "./SessionRating.css";
import { submitRating } from "../services/RatingService";

import {
  FaRegFrown,
  FaRegMeh,
  FaRegSmile
} from "react-icons/fa";

export default function SessionRating({
  onSuccess,
  submitLabel,
  allowSuccessOnError = false,
  deviceId = "arduino-device-01",
  sessionId,
}) {

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

  async function handleSubmit() {

    if (!rating) {
      setMessage(t.selectRating);
      return;
    }

    try {
      if (!sessionId) {
        if (allowSuccessOnError && onSuccess) {
          setMessage("No session found for rating");
          onSuccess();
          return;
        }

        setMessage("No session found for rating");
        return;
      }

      await submitRating({
        device_id: deviceId,
        session_id: sessionId,
        rating: rating,
        comment: ""
      });

      setMessage(t.ratingSaved);
      if (onSuccess) {
        onSuccess();
      }
    } catch (e) {

      console.error(e);
      if (allowSuccessOnError && onSuccess) {
        onSuccess();
        return;
      }

      setMessage("Failed to save rating");
    }
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

      <button
        className="rating-submit"
        onClick={handleSubmit}
      >
        {submitLabel || t.submitRating || "Submit rating"}
      </button>

      

    </div>
  );
}
