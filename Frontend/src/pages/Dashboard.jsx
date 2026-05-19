import { useEffect, useState } from "react";
import { getEnvironmentDataa } from "../services/EnvironmentService";
import SensorCard from "../components/SensorCard";
import "./Dashboard.css";
import { useLanguage } from "../context/LanguageContext";
import SessionRating from "../components/SessionRating";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [hasDevice, setHasDevice] = useState(false);
  const { t } = useLanguage();
  //get the current user
  const user = JSON.parse(localStorage.getItem("user"));
  
  useEffect(() => {
  const checkConnection = () => {
     // take the list of associations ("user devices")
    const userDevices = JSON.parse(localStorage.getItem("user_devices")) || [];
     //check if the logged in user has at least one device connected
    const connectedDevice = userDevices.find(d => d.email === user?.email);

    if (connectedDevice) {
      setHasDevice(true);
      // We only request the data if we found a device
      getEnvironmentDataa().then((res) => {
        setData(res);
      });
    } else {
      setHasDevice(false);
      setData("no_device");
    }
  };

  checkConnection();
  window.addEventListener("storage", checkConnection);

  return () => {
    window.removeEventListener("storage", checkConnection);
  };
  }, [user?.email]);

  // If there is no device connected, we display a warning message
  if (!hasDevice || data === "no_device") {
    return (
      <div className="dashboard">
        <h1>{t.dashboard}</h1>
        <div className="recommendation-card">
          <p> You don't have any devices connected. Go to Profile for setup</p>
        </div>
      </div>
    );
  }

  
  if (!data) {
  return <LoadingSpinner text={t.loading} />;
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
