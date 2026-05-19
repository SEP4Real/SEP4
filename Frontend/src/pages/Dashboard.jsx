import { useEffect, useState } from "react";
import "./Dashboard.css";
import { useLanguage } from "../context/LanguageContext";
import { getDashboardData } from "../services/DashboardService";
import SensorChart from "../components/SensorChart";
import EmptyState from "../components/EmptyState";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Dashboard() {
  const { t } = useLanguage();
  const [dashboardData, setDashboardData] = useState([]);
  const [hasDevice, setHasDevice] = useState(false);
  const [loading, setLoading] = useState(true);

  const user = JSON.parse(localStorage.getItem("user"));

  const placeholderData = [
    {
      temperature: 22,
      humidity: 45,
      co2_level: 500,
      light_level: 300,
      predicted_study_quality: 4,
      sent_at: "2026-05-18T10:00:00",
    },
    {
      temperature: 23,
      humidity: 44,
      co2_level: 650,
      light_level: 290,
      predicted_study_quality: 4,
      sent_at: "2026-05-18T10:05:00",
    },
    {
      temperature: 24,
      humidity: 42,
      co2_level: 850,
      light_level: 260,
      predicted_study_quality: 3,
      sent_at: "2026-05-18T10:10:00",
    },
    {
      temperature: 25,
      humidity: 38,
      co2_level: 1200,
      light_level: 220,
      predicted_study_quality: 3,
      sent_at: "2026-05-18T10:15:00",
    },
    {
      temperature: 27,
      humidity: 30,
      co2_level: 1700,
      light_level: 180,
      predicted_study_quality: 2,
      sent_at: "2026-05-18T10:20:00",
    },
    {
      temperature: 30,
      humidity: 24,
      co2_level: 2200,
      light_level: 120,
      predicted_study_quality: 1,
      sent_at: "2026-05-18T10:25:00",
    },
  ];

  useEffect(() => {
    const checkConnection = async () => {
      setLoading(true);

      const userDevices =
        JSON.parse(localStorage.getItem("user_devices")) || [];

      const connectedDevice = userDevices.find(
        (device) => device.email === user?.email
      );

      if (!connectedDevice) {
        setHasDevice(false);
        setLoading(false);
        return;
      }

      setHasDevice(true);

      try {
        const data = await getDashboardData();
        setDashboardData(data.length > 0 ? data : placeholderData);
      } catch (error) {
        console.error(error);
        setDashboardData(placeholderData);
      } finally {
        setLoading(false);
      }
    };

    checkConnection();
  }, [user?.email]);

  if (loading) {
    return <LoadingSpinner text={t.loading} />;
  }

  if (!hasDevice) {
    return (
      <div className="dashboard">
        <EmptyState
          icon="📡"
          title={t.noDeviceTitle}
          message={t.noDeviceMessage}
        />
      </div>
    );
  }

  const latestData = dashboardData[dashboardData.length - 1];

  if (!latestData) {
    return (
      <div className="dashboard">
        <EmptyState
          icon="📂"
          title={t.noDashboardDataTitle}
          message={t.noDashboardDataMessage}
        />
      </div>
    );
  }

  return (
    <div className="dashboard">
      <SensorChart data={dashboardData} />

      <div className="recommendation-card">
        <h2>{t.recommendation}</h2>
      </div>
    </div>
  );
}