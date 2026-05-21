import { FolderCog } from "lucide-react";
import "./EmptyState.css";

export default function EmptyState({
  icon = <FolderCog size={40} strokeWidth={1.8} />,
  title,
  message,
}) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <h2>{title}</h2>
      {message && <p>{message}</p>}
    </div>
  );
}
