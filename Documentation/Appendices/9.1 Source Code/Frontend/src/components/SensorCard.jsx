export default function SensorCard({ title, value, icon }) {
  const isStatusCard = title?.includes("Environment Status");
 
  const isGood = isStatusCard && value === "Good";
  const isBad = isStatusCard && value === "Bad";
  const extraClass = isGood ? "status-good" : isBad ? "status-bad" : "";
  

  return (
    <div className={`sensor-card ${extraClass}`} role="button" tabIndex={0}>
      <div className="sensor-title">{icon}
        <span>{title || "Loading..."}</span>
      </div>
      <div className="sensor-value">{value}</div>
    </div>
  );
}
