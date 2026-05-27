import { useEffect, useMemo, useState } from "react";
import "./Dashboard.css";
import { useLanguage } from "../context/LanguageContext";
import { getDashboardData } from "../services/DashboardService";
import { getCurrentSession } from "../services/SessionService";
import { getProfile } from "../services/ProfileService";
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

const getSessionIdStorageKey = (email) =>
  email ? `dashboard_session_id:${email}` : null;

const getStoredDeviceForUser = (email) => {
  const userDevices = JSON.parse(localStorage.getItem("user_devices")) || [];
  const connectedDevice = userDevices.find((device) => device.email === email);

  return connectedDevice?.deviceId || "";
};

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
  const [connectedDeviceId, setConnectedDeviceId] = useState("");
  const [loading, setLoading] = useState(true);

  const user = JSON.parse(localStorage.getItem("user"));

  const sessionStorageKey = getSessionStorageKey(user?.email);
  const sessionIdStorageKey = getSessionIdStorageKey(user?.email);
  const [isSessionActive, setIsSessionActive] = useState(() =>
    sessionStorageKey ? localStorage.getItem(sessionStorageKey) === "true" : false
  );
  const [sessionMessage, setSessionMessage] = useState("");
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [ratingSessionId, setRatingSessionId] = useState(() =>
    sessionIdStorageKey ? localStorage.getItem(sessionIdStorageKey) : null
  );
  const [expandedId, setExpandedId] = useState(null);
  const [filterDate, setFilterDate] = useState("");

  const clearStoredSession = () => {
    if (sessionStorageKey) {
      localStorage.removeItem(sessionStorageKey);
    }

    if (sessionIdStorageKey) {
      localStorage.removeItem(sessionIdStorageKey);
    }
  };

  const storeActiveSession = (sessionId) => {
    if (sessionStorageKey) {
      localStorage.setItem(sessionStorageKey, "true");
    }

    if (sessionIdStorageKey) {
      localStorage.setItem(sessionIdStorageKey, String(sessionId));
    }
  };

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

      let savedDeviceId = getStoredDeviceForUser(user?.email);

      try {
        const result = await getProfile();
        savedDeviceId = result.profile?.connected_device_id || savedDeviceId;
      } catch (error) {
        console.error("Error loading profile device:", error);
      }

      if (!savedDeviceId) {
        setHasDevice(false);
        setConnectedDeviceId("");
        setIsSessionActive(false);
        setRatingSessionId(null);
        setSessionMessage("");
        setDashboardData([]);
        clearStoredSession();
        setLoading(false);
        return;
      }

      setHasDevice(true);
      setConnectedDeviceId(savedDeviceId);
      setSessionMessage("");

      await loadDashboardData();

      const shouldRestoreSession =
        sessionStorageKey && localStorage.getItem(sessionStorageKey) === "true";
      const storedSessionId = sessionIdStorageKey
        ? localStorage.getItem(sessionIdStorageKey)
        : null;

      if (shouldRestoreSession && storedSessionId) {
        try {
          const currentSession = await getCurrentSession(savedDeviceId);

          if (currentSession && String(currentSession.id) === storedSessionId) {
            setRatingSessionId(currentSession.id);
            setIsSessionActive(true);
          } else {
            setIsSessionActive(false);
            setRatingSessionId(null);
            clearStoredSession();
          }
        } catch (error) {
          console.error("Error restoring active session:", error);
          setIsSessionActive(false);
          setRatingSessionId(null);
          clearStoredSession();
        }
      } else {
        setIsSessionActive(false);
        setRatingSessionId(null);
      }

      setLoading(false);
    };

    checkConnection();

    window.addEventListener("storage", checkConnection);

    return () => {
      window.removeEventListener("storage", checkConnection);
    };
  }, [user?.email, sessionStorageKey, sessionIdStorageKey]);
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

  const handleStartSession = async () => {
    if (!connectedDeviceId) {
      setSessionMessage(t.noDeviceMessage);
      return;
    }

    try {
      const currentSession = await getCurrentSession(connectedDeviceId);

      if (!currentSession) {
        setIsSessionActive(false);
        setRatingSessionId(null);
        clearStoredSession();
        setSessionMessage(t.noActiveSessionFound);
        return;
      }

      setRatingSessionId(currentSession.id);
      setIsSessionActive(true);
      storeActiveSession(currentSession.id);
      setSessionMessage("");
      await loadDashboardData();
    } catch (error) {
      console.error("Error loading active session:", error);
      setIsSessionActive(false);
      setRatingSessionId(null);
      clearStoredSession();
      setSessionMessage(t.noActiveSessionFound);
    }
  };

  const latestData = dashboardData[dashboardData.length - 1];
  const latestMetrics = normalizeDashboardRecord(latestData);

  const filteredHistory = useMemo(() => {
    const visibleHistory = filterDate
      ? dashboardData.filter((item) => {
      const { sentAt } = normalizeDashboardRecord(item);

      if (!sentAt) {
        return false;
      }

      return new Date(sentAt).toISOString().slice(0, 10) === filterDate;
    })
      : dashboardData;

    return [...visibleHistory].sort((a, b) => {
      const firstDate = normalizeDashboardRecord(a).sentAt;
      const secondDate = normalizeDashboardRecord(b).sentAt;

      return new Date(secondDate) - new Date(firstDate);
    });
  }, [dashboardData, filterDate]);

  const toggleAccordion = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (loading) {
  return <LoadingSpinner text={t.loading} />;
}

  const openRatingModal = async () => {
    if (!ratingSessionId && connectedDeviceId) {
      try {
        const currentSession = await getCurrentSession(connectedDeviceId);
        setRatingSessionId(currentSession?.id || null);
      } catch (error) {
        console.error("Error loading session for rating:", error);
        setRatingSessionId(null);
      }
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
              onClick={handleStartSession}
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
              {t.liveMonitoringActive}
            </span>
          )}
        </div>

        {!isSessionActive && (
          <p className="session-help-text">
            {sessionMessage || t.startSessionToViewLiveData}
          </p>
        )}
      </div>

      <div className="live-section-header">
        <h2>{t.historyTitle}</h2>
      </div>

      {isSessionActive && (
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
      )}

      {isSessionActive && (
      <div className="chart-card">
        <div className="chart-card-header">
          <span>Live sensor evolution</span>
        </div>
        <SensorChart data={dashboardData} />
      </div>
      )}

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
              deviceId={connectedDeviceId || DEFAULT_DEVICE_ID}
              sessionId={ratingSessionId}
              onSuccess={() => {
                setShowRatingModal(false);
                setIsSessionActive(false);
                setRatingSessionId(null);
                clearStoredSession();
              }}
            />
          </div>
        </div>
      )}

      {isSessionActive && (
      <div className={`recommendation-card ${recommendation.status}`}>

  <div className="recommendation-emoji">
    {recommendation.emoji}
  </div>

  <h2>{t.recommendation}</h2>

  <h3>{recommendation.title}</h3>

  <p>{recommendation.message}</p>

</div>
      )}
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
