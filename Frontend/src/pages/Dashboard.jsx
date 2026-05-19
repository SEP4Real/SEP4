import { useEffect, useMemo, useState } from "react";
import "./Dashboard.css";
import { useLanguage } from "../context/LanguageContext";
import { getDashboardData } from "../services/DashboardService";
import SensorChart from "../components/SensorChart";
import SessionRating from "../components/SessionRating";
import { CalendarRange, CirclePlay, Clock3, MonitorX } from "lucide-react";

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

export default function Dashboard() {
  const { t } = useLanguage();
  const [dashboardData, setDashboardData] = useState([]);
  const [hasDevice, setHasDevice] = useState(false);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [expandedId, setExpandedId] = useState(null);
  const [filterDate, setFilterDate] = useState("");

  const user = JSON.parse(localStorage.getItem("user"));

  const loadDashboardData = async () => {
    try {
      const data = await getDashboardData();
      setDashboardData(data.length > 0 ? data : placeholderData);
    } catch (e) {
      console.error(e);
      setDashboardData(placeholderData);
    }
  };

  useEffect(() => {
    const checkConnection = async () => {
      const userDevices =
        JSON.parse(localStorage.getItem("user_devices")) || [];

      const connectedDevice = userDevices.find((d) => d.email === user?.email);

      if (!connectedDevice) {
        setHasDevice(false);
        setDashboardData([]);
        return;
      }

      setHasDevice(true);
      await loadDashboardData();
    };

    checkConnection();
    window.addEventListener("storage", checkConnection);

    return () => {
      window.removeEventListener("storage", checkConnection);
    };
  }, [user?.email]);

  useEffect(() => {
    if (!hasDevice || !isSessionActive) {
      return undefined;
    }

    const interval = setInterval(loadDashboardData, 60000);

    return () => {
      clearInterval(interval);
    };
  }, [hasDevice, isSessionActive]);

  const latestData = dashboardData[dashboardData.length - 1];

  const filteredHistory = useMemo(() => {
    if (!filterDate) {
      return dashboardData;
    }

    return dashboardData.filter((item) => {
      if (!item.sent_at) {
        return false;
      }

      return new Date(item.sent_at).toISOString().slice(0, 10) === filterDate;
    });
  }, [dashboardData, filterDate]);

  const toggleAccordion = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (!hasDevice) {
    return (
      <div className="dashboard">
        <div className="recommendation-card">
          <p>Warning: you do not have any devices connected. Go to Profile for setup.</p>
        </div>
      </div>
    );
  }

  if (!latestData) {
    return <p>{t.loading}</p>;
  }

  return (
    <div className="dashboard">
      <h1>{t.dashboardTitle || t.dashboard}</h1>

      <div className="session-control-card">
        {!isSessionActive ? (
          <button
            className="session-btn start"
            onClick={() => {
              setIsSessionActive(true);
              loadDashboardData();
            }}
          >
            <CirclePlay size={18} /> {t.StartSession}
          </button>
        ) : (
          <button
            className="session-btn stop"
            onClick={() => setIsSessionActive(false)}
          >
            <MonitorX size={18} /> {t.StopSession}
          </button>
        )}

        {isSessionActive && (
          <span className="live-status-container">
            <span className="live-dot"></span>
            Live Monitoring Active...
          </span>
        )}
      </div>

      <SensorChart data={dashboardData} />

      <div className="recommendation-card">
        <h2>{t.recommendation}</h2>
        <p>Latest predicted study quality: {latestData.predicted_study_quality}/5</p>
      </div>

      <SessionRating />

      <div className="details-card-container">
        <div className="details-card-header">
          <h2>{t.detailedHistory}</h2>
          <input
            type="date"
            className="calendar-input"
            onChange={(e) => setFilterDate(e.target.value)}
          />
        </div>

        <div className="accordion-list">
          {filteredHistory.map((item) => (
            <div
              key={item.id || item.sent_at}
              className={`accordion-row ${expandedId === item.id ? "active" : ""}`}
            >
              <div
                className="row-main"
                onClick={() => toggleAccordion(item.id || item.sent_at)}
              >
                <span className="row-title">
                  <CalendarRange size={16} />{" "}
                  {new Date(item.sent_at).toLocaleDateString()} |{" "}
                  <Clock3 size={16} />{" "}
                  {new Date(item.sent_at).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
                <span className="arrow">
                  {expandedId === (item.id || item.sent_at) ? "^" : "v"}
                </span>
              </div>

              {expandedId === (item.id || item.sent_at) && (
                <div className="row-content">
                  <div className="sensor-details-grid">
                    <div className="sensor-detail-item">
                      {t.tempShort}: <strong>{item.temperature} °C</strong>
                    </div>
                    <div className="sensor-detail-item">
                      {t.humShort}: <strong>{item.humidity} %</strong>
                    </div>
                    <div className="sensor-detail-item">
                      CO2: <strong>{item.co2_level} ppm</strong>
                    </div>
                    <div className="sensor-detail-item">
                      {t.light}: <strong>{item.light_level} lx</strong>
                    </div>
                    <div className="sensor-detail-item">
                      Study quality:{" "}
                      <strong>{item.predicted_study_quality}/5</strong>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}

          {filteredHistory.length === 0 && (
            <p className="no-records-text">
              No recordings found for this date.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
