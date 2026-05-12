import { useEffect, useState } from "react";
import { getEnvironmentDataa } from "../services/EnvironmentService";
import SensorCard from "../components/SensorCard";
import "./Dashboard.css";
import { useLanguage } from "../context/LanguageContext";
import SessionRating from "../components/SessionRating";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const { t } = useLanguage();

  
  useEffect(() => {
    getEnvironmentDataa().then((res) => {
      setData(res);
    });
  }, []);

  if (!data) {
    return <p>{t.loading}</p>;
  }

  
  return (
    <div className="dashboard">
      <h1>{t.dashboard}</h1>

      <div className="dashboard-grid">

        <SensorCard title={t.temperature} value={data.temperature + " °C"} />
        <SensorCard title={t.humidity} value={data.humidity + " %"} />
        <SensorCard title={t.co2Level} value={data.co2Level + " ppm"} />
        <SensorCard title={t.lightLevel} value={data.lightLevel + " lx"} />
        <SensorCard 
        title={t.suitabilityLevel}
        value={(data.suitabilityLevel * 100).toFixed(0) + "%"}/>
        <SensorCard
        title={t.predictedSuitability}
        value={(data.predictedSuitabilityLevel * 100).toFixed(0) + "%"}/>
        <SensorCard
        title={t.trend}
        value={data.predictedTrend === 1
            ? t.improving
            : t.declining}/>
        <SensorCard
        title={t.environmentStatus}
        value={data.environmentStatus === 1 ? t.good : t.bad}/>

      </div>

<div className="recommendation-card">
  <h2>{t.recommendation}</h2>

  <p>
    {data.recommendation}
  </p>
</div>
<SessionRating />

    </div>
  );
}
