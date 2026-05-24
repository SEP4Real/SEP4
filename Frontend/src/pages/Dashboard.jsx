import { useEffect, useMemo, useState } from "react";
import "./Dashboard.css";
import { useLanguage } from "../context/LanguageContext";
import { getDashboardData } from "../services/DashboardService";
import { getDeviceSessions } from "../services/SessionService";
import SensorChart from "../components/SensorChart";
import SessionRating from "../components/SessionRating";
import LoadingSpinner from "../components/LoadingSpinner";
import SensorCard from "../components/SensorCard";
import EmptyState from "../components/EmptyState";
import {
  CalendarRange,
  CirclePlay,
  Clock3,
  MonitorX,
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

const RATING_POPUP_DELAY_MS = 60 * 60 * 1000;
const DEFAULT_DEVICE_ID = "arduino-device-01";

const getSessionStorageKey = (email) =>
  email ? `dashboard_session_active:${email}` : null;

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
  const [loading, setLoading] = useState(true);

  const user = JSON.parse(localStorage.getItem("user"));

  const sessionStorageKey = getSessionStorageKey(user?.email);
  const [isSessionActive, setIsSessionActive] = useState(() => {
    return sessionStorageKey
      ? localStorage.getItem(sessionStorageKey) === "true"
      : false;
  });
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [ratingSessionId, setRatingSessionId] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [filterDate, setFilterDate] = useState("");

  const loadDashboardData = async () => {
    try {
      const data = await getDashboardData();

      const records =
        Array.isArray(data) && data.length > 0
          ? data
          : placeholderData;

      setDashboardData(records.map(prepareDashboardRecord));
    } catch (e) {
      console.error(e);
      setDashboardData(placeholderData.map(prepareDashboardRecord));
    }
  };

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
        setIsSessionActive(false);
        setRatingSessionId(null);
        setDashboardData([]);
        setLoading(false);
        return;
      }

      setHasDevice(true);

      await loadDashboardData();

      setLoading(false);
    };

    checkConnection();

    window.addEventListener("storage", checkConnection);

    return () => {
      window.removeEventListener("storage", checkConnection);
    };
  }, [user?.email]);
  useEffect(() => {
    if (!hasDevice) {
      return undefined;
    }

    const interval = setInterval(loadDashboardData, 60000);

    return () => {
      clearInterval(interval);
    };
  }, [hasDevice]);

  useEffect(() => {
    if (!isSessionActive) {
      return undefined;
    }

    const ratingTimer = setTimeout(() => {
      openRatingModal();
    }, RATING_POPUP_DELAY_MS);

    return () => {
      clearTimeout(ratingTimer);
    };
  }, [isSessionActive]);

  useEffect(() => {
    if (!sessionStorageKey) {
      return;
    }

    localStorage.setItem(sessionStorageKey, String(isSessionActive));
  }, [isSessionActive, sessionStorageKey]);

  const latestData = dashboardData[dashboardData.length - 1];
  const latestMetrics = normalizeDashboardRecord(latestData);

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

  if (loading) {
  return <LoadingSpinner text={t.loading} />;
}

  const openRatingModal = async () => {
    try {
      const sessions = await getDeviceSessions(DEFAULT_DEVICE_ID);
      const latestSession = [...sessions].sort((a, b) => {
        return new Date(b.startedAt || b.started_at) - new Date(a.startedAt || a.started_at);
      })[0];

      setRatingSessionId(latestSession?.id || null);
    } catch (error) {
      console.error("Error loading session for rating:", error);
      setRatingSessionId(null);
    }

    setShowRatingModal(true);
  };

  if (!hasDevice) {
    return (
      <div className="dashboard">
        <EmptyState
          title={t.noDeviceTitle}
          message={t.noDeviceMessage}
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="dashboard">
        <LoadingSpinner text="Loading environment data..." />
      </div>
    );
  }

  if (!latestData) {
    return (
      <div className="dashboard">
        <EmptyState
          title={t.noDashboardDataTitle}
          message={t.noDashboardDataMessage}
        />
      </div>
    );
  }

  const getRecommendation = (quality) => {
    if (quality >= 4) {
     return {
  status: "good",
  emoji: "😁",
  title: t.recommendationGoodTitle,
  message: t.recommendationGoodMessage,
};
    }

    if (quality === 3) {
      return {
  status: "moderate",
  emoji: "😐",
  title: t.recommendationModerateTitle,
  message: t.recommendationModerateMessage,
};
    }
return {
  status: "poor",
  emoji: "😭",
  title: t.recommendationPoorTitle,
  message: t.recommendationPoorMessage,
};
  };

  const recommendation = getRecommendation(latestData.predicted_study_quality);

  return (
    <div className="dashboard">
      <div className="dashboard-hero">
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
              onClick={openRatingModal}
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
      </div>

      <div className="live-section-header">
        <h2>{t.historyTitle}</h2>
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
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-card-header">
          <span>Live sensor evolution</span>
        </div>
        <SensorChart data={dashboardData} />
      </div>

      {showRatingModal && (
        <div className="rating-modal">
          <div className="rating-modal-content">
            <button
              type="button"
              className="close-rating-modal"
              onClick={() => setShowRatingModal(false)}
            >
              ×
            </button>

            <SessionRating
              submitLabel="Submit rating"
              allowSuccessOnError
              deviceId={DEFAULT_DEVICE_ID}
              sessionId={ratingSessionId}
              onSuccess={() => {
                setShowRatingModal(false);
                setIsSessionActive(false);
                setRatingSessionId(null);
              }}
            />
          </div>
        </div>
      )}

      <div className={`recommendation-card ${recommendation.status}`}>

  <div className="recommendation-emoji">
    {recommendation.emoji}
  </div>

  <h2>{t.recommendation}</h2>

  <h3>{recommendation.title}</h3>

  <p>{recommendation.message}</p>

</div>
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
