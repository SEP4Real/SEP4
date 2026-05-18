import { useEffect, useState } from "react";
import SensorCard from "../components/SensorCard";
import "./Dashboard.css";
import { useLanguage } from "../context/LanguageContext";
import SessionRating from "../components/SessionRating";
import { getDashboardData } from "../services/DashboardService";

export default function Dashboard() {
  const { t } = useLanguage();
  const [dashboardData, setDashboardData] = useState([]);
  console.log(dashboardData);
  

  // temporary -- until db has data
  const placeholderData = [
    {
      temperature: 22,
      humidity: 45,
      co2_level: 500,
      light_level: 300,
      predicted_study_quality: 4,
      sent_at: "2026-05-18T10:00:00"
    },

    {
      temperature: 99,
      humidity: 12,
      co2_level: 9999,
      light_level: 1,
      predicted_study_quality: 1,
      sent_at: "2026-05-18T10:20:00"
    }
  ];

  useEffect(() => {

    const loadDashboardData = async () => {
      try {
        const data = await getDashboardData();

        // temporary -- will be replaced with setDashboardData(data);
        setDashboardData(
          data.length > 0 ? data : placeholderData
        );

        // 

      } catch (e) {
        console.error(e);

        // temporary -- will be replaced with setDashboardData([]);
        setDashboardData(placeholderData);
      }
    };

    loadDashboardData();

  }, []);

  
  const latestData =
        dashboardData[dashboardData.length - 1];
    if (!latestData) {return <p>{t.loading}</p>;}

  
  
  return (
    <div className="dashboard">
      <h1>{t.dashboard}</h1>
      <div className="dashboard-grid">

    <SensorCard
      title={t.temperature}
      value={latestData.temperature + " °C"}/>

    <SensorCard
      title={t.humidity}
      value={latestData.humidity + " %"}/>

    <SensorCard
      title={t.co2Level}
      value={latestData.co2_level + " ppm"}/>

    <SensorCard
      title={t.lightLevel}
      value={latestData.light_level + " lx"}/>

    <SensorCard
      title={t.environmentStatus}
      value={
        latestData.predicted_study_quality >= 4
          ? t.good
          : latestData.predicted_study_quality >= 3
          ? t.okay
          : t.bad}/>

    <SensorCard
      title={t.predictedSuitability}
      value={latestData.predicted_study_quality + "/5"}
    />

  </div>

<div className="recommendation-card">
  <h2>{t.recommendation}</h2>

  <p>
    {
    latestData.predicted_study_quality >= 4
      ? "Good study conditions"
      : latestData.predicted_study_quality >= 3
      ? "Conditions are acceptable"
      : "Environment quality is decreasing"
  }
  </p>
</div>
<SessionRating />

    </div>
  );
}
