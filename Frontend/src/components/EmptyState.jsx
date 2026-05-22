import "./EmptyState.css";

export default function EmptyState({ icon = "📁", title, message }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <h2>{title}</h2>
      {message && <p>{message}</p>}
    </div>
  );
}