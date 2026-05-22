import "./LoadingSpinner.css";

export default function LoadingSpinner({ text }) {
  return (
    <div className="loading-spinner-container">
      <div className="emoji-spinner">⏳</div>
      <p>{text}</p>
    </div>
  );
}