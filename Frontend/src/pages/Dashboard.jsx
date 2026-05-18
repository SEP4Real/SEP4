import { useEffect, useState } from "react";
import { getEnvironmentDataa } from "../services/EnvironmentService";
import SensorCard from "../components/SensorCard";
import "./Dashboard.css";
import { useLanguage } from "../context/LanguageContext";
import SessionRating from "../components/SessionRating";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  TriangleAlert,
  CirclePlay,
  MonitorX,
  Thermometer,
  Droplets,
  Fan,
  Lightbulb,
  Clock3,
  CalendarRange,
  ArrowBigUp,
  ArrowBigDown,
} from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [hasDevice, setHasDevice] = useState(false);
  const { t } = useLanguage();

  const [isSessionActive, setIsSessionActive] = useState(false);
  const [historyData, setHistoryData] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [filterDate, setFilterDate] = useState("");

  const user = JSON.parse(localStorage.getItem("user"));

  const loadHistoryData = async () => {
    try {
      console.log("Fetching real data from DB...");
      const rawData = await getEnvironmentDataa();

      if (rawData && Array.isArray(rawData)) {
        const formattedData = rawData.map((item) => ({
          id: item.id,
          temperature: item.temperature,
          humidity: item.humidity,
          co2: item.co2Level,
          light: item.lightLevel,
          dateValue: new Date(item.sentAt).toISOString().slice(0, 10),
          date: new Date(item.sentAt).toLocaleDateString(),
          time: new Date(item.sentAt).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        }));
        setHistoryData(formattedData);

        if (formattedData.length > 0) {
          const latestRecord = rawData[rawData.length - 1];
          setData(latestRecord);
        }
      }
    } catch (error) {
      console.error("Data processing error:", error);
    }
  };

  useEffect(() => {
    const checkConnection = () => {
      const userDevices =
        JSON.parse(localStorage.getItem("user_devices")) || [];
      const connectedDevice = userDevices.find((d) => d.email === user?.email);

      if (connectedDevice) {
        setHasDevice(true);
        loadHistoryData();
        getEnvironmentDataa().then((res) => {
          setData(res);
        });
      } else {
        setHasDevice(false);
        setData("no_device");
        setHistoryData([]);
      }
    };

    checkConnection();
    window.addEventListener("storage", checkConnection);

    return () => {
      window.removeEventListener("storage", checkConnection);
    };
  }, [user?.email]);

  useEffect(() => {
    let interval = null;
    if (hasDevice && isSessionActive) {
      interval = setInterval(() => {
        loadHistoryData();
      }, 60000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [hasDevice, isSessionActive]);

  // Start / Stop
  const handleStartSession = () => {
    setIsSessionActive(true);
    alert("Measurement session started! Data is now updating live.");
    loadHistoryData();
  };

  const handleStopSession = () => {
    setIsSessionActive(false);
    alert("Session stopped. Data saved to your history below.");
  };

  const toggleAccordion = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const filteredHistory = filterDate
    ? historyData.filter((item) => item.dateValue === filterDate)
    : historyData;

  if (!hasDevice || data === "no_device") {
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

  if (!data) {
    return <p>{t.loading}</p>;
  }

  return (
    <div className="dashboard">
      <h1>{t.dashboardTitle}</h1>

      {/*  START / STOP */}
      <div className="session-control-card">
        {!isSessionActive ? (
          <button className="session-btn start" onClick={handleStartSession}>
            <CirclePlay /> {t.StartSession}
          </button>
        ) : (
          <button className="session-btn stop" onClick={handleStopSession}>
            <MonitorX /> {t.StopSession}
          </button>
        )}

        {isSessionActive && (
          <span className="live-status-container">
            <span className="live-dot"></span>
            Live Monitoring Active...
          </span>
        )}
      </div>

      <div className="dashboard-grid">
        <SensorCard
          title={t.temperature}
          value={data.temperature + " °C"}
          icon={<Thermometer className="sensor-icon" />}
        />
        <SensorCard
          title={t.humidity}
          value={data.humidity + " %"}
          icon={<Droplets className="sensor-icon" />}
        />
        <SensorCard
          title={t.co2Level}
          value={data.co2Level + " ppm"}
          icon={<Fan className="sensor-icon" />}
        />
        <SensorCard
          title={t.lightLevel}
          value={data.lightLevel + " lx"}
          icon={<Lightbulb className="sensor-icon" />}
        />
        <SensorCard
          title={t.suitabilityLevel}
          value={(data.suitabilityLevel * 100).toFixed(0) + "%"}
        />
        <SensorCard
          title={t.trend}
          value={data.predictedTrend === 1 ? t.improving : t.declining}
        />
      </div>

      <div className="recommendation-card">
        <h2>{t.recommendation}</h2>

        <p>{data.recommendation}</p>
      </div>
      <SessionRating />

      {/* GRAPH */}
      <div className="chart-card-container">
        <h4 className="chart-title">{t.evolutionTrend}</h4>

        <div className="chart-wrapper">
          <ResponsiveContainer width="99%" height="100%">
            <LineChart
              data={filteredHistory}
              margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#eee"
              />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="temperature"
                stroke="#4CAF50"
                strokeWidth={4}
                dot={{ r: 6 }}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* CALENDAR */}
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
              key={item.id}
              className={`accordion-row ${expandedId === item.id ? "active" : ""}`}
            >
              <div
                className="row-main"
                onClick={() => toggleAccordion(item.id)}
              >
                <span className="row-title">
                  <CalendarRange /> {item.date} | <Clock3 /> {item.time}
                </span>
                <span className="arrow">
                  {expandedId === item.id
                    ? "<ArrowBigUp />"
                    : "<ArrowBigDown />"}
                </span>
              </div>

              {expandedId === item.id && (
                <div className="row-content">
                  <div className="sensor-details-grid">
                    <div className="sensor-detail-item">
                      {t.tempShort}: <strong>{item.temperature}°C</strong>
                    </div>
                    <div className="sensor-detail-item">
                      {t.humShort}: <strong>{item.humidity}%</strong>
                    </div>
                    <div className="sensor-detail-item">
                      CO2: <strong>{item.co2} ppm</strong>
                    </div>
                    <div className="sensor-detail-item">
                      {t.light}: <strong>{item.light} lx</strong>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}

          {filteredHistory.length === 0 && (
            <p className="no-records-text">
              No recordings found for this configuration.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
