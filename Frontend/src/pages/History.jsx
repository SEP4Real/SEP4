import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { mockHistory } from "../MockData";
import "./History.css";
import "../index.css";

const History = () => {
  const [data, setData] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [filterDate, setFilterDate] = useState("");

  useEffect(() => {
    setData(mockHistory);
  }, []);

  const toggleAccordion = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const filteredData = filterDate 
    ? data.filter(item => item.date === filterDate)
    : data;


  const latest = filteredData.length > 0 ? filteredData[filteredData.length - 1] : {};

  return (
    <div className="history-page">
      <div className="content-wrapper">
        
        {/*sec1*/}
        {/* SEC 1:  (Stat Cards) */}
        <section className="indicators-section">
        <div className="indicators-header">
            <h2 className="title">Real-time Environmental Monitoring</h2>
        </div>

        <div className="indicators-grid">
            <div className="indicator-card">
            <span className="card-icon">🌡️</span>
            <div className="card-info">
                <p>Temperature</p>
                <h3>{latest.temperature || "--"} °C</h3>
            </div>
            </div>
            <div className="indicator-card">
            <span className="card-icon">💧</span>
            <div className="card-info">
                <p>Humidity</p>
                <h3>{latest.humidity || "--"} %</h3>
            </div>
            </div>
            <div className="indicator-card">
            <span className="card-icon">💨</span>
            <div className="card-info">
                <p>CO2 Level</p>
                <h3>{latest.co2 || "--"} ppm</h3>
            </div>
            </div>
            <div className="indicator-card">
            <span className="card-icon">💡</span>
            <div className="card-info">
                <p>Light</p>
                <h3>{latest.light || "--"} lx</h3>
            </div>
            </div>
        </div>
        </section>

        {/* SEC 2:  General Grafic */}
        <div className="chart-card">
        <h4>Evolution Trend</h4>
        {/**/}
        <div style={{ width: '100%', height: '300px', position: 'relative' }}>
            <ResponsiveContainer width="99%" height="100%">
            <LineChart 
                data={filteredData} 
                margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
            >
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee" />
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

        {/* SEC 3: Detailed History*/}
        <div className="details-card">
          <div className="details-header">
            <h2>Detailed History</h2>
            <input 
              type="date" 
              className="calendar-input" 
              onChange={(e) => setFilterDate(e.target.value)} 
            />
          </div>

          <div className="accordion-list">
            {filteredData.map((item) => (
              <div key={item.id} className={`accordion-row ${expandedId === item.id ? 'active' : ''}`}>
                <div className="row-main" onClick={() => toggleAccordion(item.id)}>
                  <span className="row-title">📅 {item.date} | 🕒 {item.time}</span>
                  <span className="arrow">{expandedId === item.id ? '▲' : '▼'}</span>
                </div>

                {/* Rendering cond*/}
                {expandedId === item.id && (
                  <div className="row-content">
                    <div className="sensor-grid">
                      <div className="sensor-item">Temp: <strong>{item.temperature}°C</strong></div>
                      <div className="sensor-item">Hum: <strong>{item.humidity}%</strong></div>
                      <div className="sensor-item">CO2: <strong>{item.co2} ppm</strong></div>
                      <div className="sensor-item">Light: <strong>{item.light} lx</strong></div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default History;