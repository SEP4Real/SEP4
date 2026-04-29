export default function SensorCard({ title, value }) {
  const isStatusCard = title.includes("Environment Status");

  const isGood = isStatusCard && value === "Good";
  const isBad = isStatusCard && value === "Bad";

  const extraClass = isGood ? "status-good" : isBad ? "status-bad" : "";

  return (
    <div className={`sensor-card ${extraClass}`}>
      <div className="sensor-title">{title}</div>
      <div className="sensor-value">{value}</div>
    </div>
  );
}
