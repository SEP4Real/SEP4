import { useEffect, useState } from "react";
import { getEnvironmentDataa } from "../services/EnvironmentService";
import SensorCard from "../components/SensorCard";
import "./Dashboard.css";

export default function StudentDashboard() {
  const [data, setData] = useState(null);

  
  useEffect(() => {
    getEnvironmentDataa().then((res) => {
      setData(res);
    });
  }, []);

  if (!data) {
    return <p>Loading environment data...</p>;
  }

  
  return (
    <div className="dashboard">
      <h1>Student Dashboard</h1>

      <div className="dashboard-grid">

        <SensorCard title="Temperature " value={data.temperature + " °C"} />
        <SensorCard title="Humidity " value={data.humidity + " %"} />
        <SensorCard title="CO₂ Level " value={data.co2Level + " ppm"} />
        <SensorCard title="Light Level " value={data.lightLevel + " lx"} />
        <SensorCard title="Noise Level " value={data.noiseLevel + " dB"} />
        <SensorCard 
        title="Suitability Level "
        value={(data.suitabilityLevel * 100).toFixed(0) + "%"}/>
        <SensorCard
        title="Predicted Suitability "
        value={(data.predictedSuitabilityLevel * 100).toFixed(0) + "%"}/>
        <SensorCard
        title="Trend "
        value={data.predictedTrend === 1
            ? "Improving"
            : "Declining"}/>
        <SensorCard
        title="Environment Status "
        value={data.environmentStatus === 1 ? "Good" : "Bad"}/>

      </div>
    </div>
  );
}
