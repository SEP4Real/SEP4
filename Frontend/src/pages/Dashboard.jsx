import { useEffect, useState } from "react";
import SensorCard from "../components/SensorCard";
import "./Dashboard.css";
import { useLanguage } from "../context/LanguageContext";
import SessionRating from "../components/SessionRating";
import { getDashboardData } from "../services/DashboardService";
import SensorChart from "../components/SensorChart";

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
      temperature: 23,
      humidity: 44,
      co2_level: 650,
      light_level: 290,
      predicted_study_quality: 4,
      sent_at: "2026-05-18T10:05:00"
    },
    {
      temperature: 24,
      humidity: 42,
      co2_level: 850,
      light_level: 260,
      predicted_study_quality: 3,
      sent_at: "2026-05-18T10:10:00"
    },
    {
      temperature: 25,
      humidity: 38,
      co2_level: 1200,
      light_level: 220,
      predicted_study_quality: 3,
      sent_at: "2026-05-18T10:15:00"
    },
    {
      temperature: 27,
      humidity: 30,
      co2_level: 1700,
      light_level: 180,
      predicted_study_quality: 2,
      sent_at: "2026-05-18T10:20:00"
    },
    {
      temperature: 30,
      humidity: 24,
      co2_level: 2200,
      light_level: 120,
      predicted_study_quality: 1,
      sent_at: "2026-05-18T10:25:00"
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
      <SensorChart data={dashboardData} />
      <SessionRating />

    </div>
  );
}
