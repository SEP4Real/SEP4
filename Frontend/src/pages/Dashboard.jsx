import { useEffect, useMemo, useState } from "react";
import "./Dashboard.css";
import { useLanguage } from "../context/LanguageContext";
import { getDashboardData } from "../services/DashboardService";
import SensorChart from "../components/SensorChart";
import SessionRating from "../components/SessionRating";
import SensorCard from "../components/SensorCard";
import {
  CalendarRange,
  CheckCircle2,
  CirclePlay,
  Clock3,
  MonitorX,
  TriangleAlert,
  Thermometer,
  Droplets,
  Fan,
  Lightbulb,
} from "lucide-react";

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

const normalizeDashboardRecord = (item = {}) => {
  const predictedStudyQuality =
    item.predictedStudyQuality ?? item.predicted_study_quality ?? 0;
  const suitabilityLevel =
    item.suitabilityLevel ?? (predictedStudyQuality ? predictedStudyQuality / 5 : 0);

  return {
    id: item.id,
    temperature: item.temperature ?? 0,
    humidity: item.humidity ?? 0,
    co2Level: item.co2Level ?? item.co2_level ?? 0,
    lightLevel: item.lightLevel ?? item.light_level ?? 0,
    suitabilityLevel,
    predictedTrend: item.predictedTrend ?? 0,
    predictedStudyQuality,
    sentAt: item.sentAt ?? item.sent_at,
  };
};

const prepareDashboardRecord = (item = {}) => {
  const record = normalizeDashboardRecord(item);

  return {
    ...item,
    co2_level: record.co2Level,
    light_level: record.lightLevel,
    predicted_study_quality: record.predictedStudyQuality,
    sent_at: record.sentAt,
    co2Level: record.co2Level,
    lightLevel: record.lightLevel,
    suitabilityLevel: record.suitabilityLevel,
    predictedTrend: record.predictedTrend,
    predictedStudyQuality: record.predictedStudyQuality,
    sentAt: record.sentAt,
  };
};

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
      const records = Array.isArray(data) && data.length > 0 ? data : placeholderData;
      setDashboardData(records.map(prepareDashboardRecord));
    } catch (e) {
      console.error(e);
      setDashboardData(placeholderData.map(prepareDashboardRecord));
    }
  };

  useEffect(() => {
    const checkConnection = async () => {
      const userDevices = JSON.parse(localStorage.getItem("user_devices")) || [];
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
  const latestMetrics = normalizeDashboardRecord(latestData);
  const recommendationText =
    latestMetrics.predictedStudyQuality >= 4
      ? "Conditions look good for studying. Keep monitoring the room while the session is active."
      : "Conditions are getting weaker. Try adjusting light, airflow, or room temperature before continuing.";

  const filteredHistory = useMemo(() => {
    if (!filterDate) {
      return dashboardData;
    }

    return dashboardData.filter((item) => {
      const { sentAt } = normalizeDashboardRecord(item);

      if (!sentAt) {
        return false;
      }

      return new Date(sentAt).toISOString().slice(0, 10) === filterDate;
    });
  }, [dashboardData, filterDate]);

  const toggleAccordion = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (!hasDevice) {
    return (
      <div className="dashboard">
        <h1>{t.dashboard}</h1>
        <div className="recommendation-card">
          <p>
            <TriangleAlert /> You don't have any devices connected. Go to
            Profile for setup
          </p>
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

      <div className="dashboard-overview">
        <div className="dashboard-grid">
          <SensorCard
            title={t.temperature}
            value={`${latestMetrics.temperature} °C`}
            icon={<Thermometer className="sensor-icon" />}
          />
          <SensorCard
            title={t.humidity}
            value={`${latestMetrics.humidity} %`}
            icon={<Droplets className="sensor-icon" />}
          />
          <SensorCard
            title={t.co2Level}
            value={`${latestMetrics.co2Level} ppm`}
            icon={<Fan className="sensor-icon" />}
          />
          <SensorCard
            title={t.lightLevel}
            value={`${latestMetrics.lightLevel} lx`}
            icon={<Lightbulb className="sensor-icon" />}
          />
          <SensorCard
            title={t.suitabilityLevel}
            value={`${(latestMetrics.suitabilityLevel * 100).toFixed(0)}%`}
          />
          <SensorCard
            title={t.trend}
            value={latestMetrics.predictedTrend === 1 ? t.improving : t.declining}
          />
        </div>

        <div className="recommendation-card overview-recommendation">
          <span className="recommendation-icon">
            <CheckCircle2 size={22} />
          </span>
          <div>
            <h2>{t.recommendation}</h2>
            <p>{recommendationText}</p>
            <strong>
              Study quality: {latestMetrics.predictedStudyQuality}/5
            </strong>
          </div>
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-card-header">
          <h2>{t.historyTitle || "Environmental Monitoring"}</h2>
          <span>Live sensor evolution</span>
        </div>
        <SensorChart data={dashboardData} />
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
          {filteredHistory.map((item) => {
            const record = normalizeDashboardRecord(item);
            const rowId = record.id || record.sentAt;

            return (
              <div
                key={rowId}
                className={`accordion-row ${expandedId === rowId ? "active" : ""}`}
              >
                <div className="row-main" onClick={() => toggleAccordion(rowId)}>
                  <span className="row-title">
                    <CalendarRange size={16} />{" "}
                    {new Date(record.sentAt).toLocaleDateString()} |{" "}
                    <Clock3 size={16} />{" "}
                    {new Date(record.sentAt).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                  <span className="arrow">{expandedId === rowId ? "^" : "v"}</span>
                </div>

                {expandedId === rowId && (
                  <div className="row-content">
                    <div className="sensor-details-grid">
                      <div className="sensor-detail-item">
                        {t.tempShort}: <strong>{record.temperature} °C</strong>
                      </div>
                      <div className="sensor-detail-item">
                        {t.humShort}: <strong>{record.humidity} %</strong>
                      </div>
                      <div className="sensor-detail-item">
                        CO2: <strong>{record.co2Level} ppm</strong>
                      </div>
                      <div className="sensor-detail-item">
                        {t.light}: <strong>{record.lightLevel} lx</strong>
                      </div>
                      <div className="sensor-detail-item">
                        Study quality: <strong>{record.predictedStudyQuality}/5</strong>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}

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
