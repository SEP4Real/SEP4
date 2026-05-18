import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer} from "recharts";
import { useState } from "react";
import "./SensorChart.css";

export default function SensorChart({ data }) {

    const [visibleLines, setVisibleLines] = useState({
    temperature: true,
    humidity: true,
    co2_level: true,
    light_level: true
    });

  return (
    <div className="chart-wrapper">
        <div className="chart-controls">

    <button
      className={`chart-toggle temperature ${
        visibleLines.temperature ? "active" : ""
      }`}
      onClick={() =>
        setVisibleLines(prev => ({
          ...prev,
          temperature: !prev.temperature
        }))
      }
    >
      Temperature
    </button>

    <button
      className={`chart-toggle humidity ${
        visibleLines.humidity ? "active" : ""
      }`}
      onClick={() =>
        setVisibleLines(prev => ({
          ...prev,
          humidity: !prev.humidity
        }))
      }
    >
      Humidity
    </button>

    <button
      className={`chart-toggle co2_level ${
        visibleLines.co2_level ? "active" : ""
      }`}
      onClick={() =>
        setVisibleLines(prev => ({
          ...prev,
          co2_level: !prev.co2_level
        }))
      }
    >
      CO₂
    </button>

    <button
      className={`chart-toggle light_level ${
        visibleLines.light_level ? "active" : ""
      }`}
      onClick={() =>
        setVisibleLines(prev => ({
          ...prev,
          light_level: !prev.light_level
        }))
      }
    >
      Light
    </button>

    </div>
      <ResponsiveContainer>

        <LineChart data={data}>

          <CartesianGrid strokeDasharray="3 3" />

          <XAxis
            dataKey="sent_at"
            tickFormatter={(value) =>
                new Date(value).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit"
                })
            }
            />

          <YAxis />

          <Tooltip content={<CustomTooltip />} />

          {visibleLines.temperature && (
        <Line
            type="monotone"
            dataKey="temperature"
            name="Temperature"
            stroke="#8BE78B"
            strokeWidth={3}
            dot={false}
        />
        )}

        {visibleLines.humidity && (
        <Line
            type="monotone"
            dataKey="humidity"
            name="Humidity"
            stroke="#4DA6FF"
            strokeWidth={3}
            dot={false}
        />
        )}

        {visibleLines.co2_level && (
        <Line
            type="monotone"
            dataKey="co2_level"
            name="CO₂"
            stroke="#C77DFF"
            strokeWidth={3}
            dot={false}
        />
        )}

        {visibleLines.light_level && (
        <Line
            type="monotone"
            dataKey="light_level"
            name="Light"
            stroke="#FFD166"
            strokeWidth={3}
            dot={false}
        />
        )}

        <Line
        type="monotone"
        dataKey="predicted_study_quality"
        name="State"
        stroke="#FF5DA2"
        strokeWidth={4}
        dot={false}
        />

        </LineChart>

      </ResponsiveContainer>
    </div>
  );
}

function CustomTooltip({ active, payload, label }) {

  if (!active || !payload || !payload.length) {
    return null;
  }

  const values = {};

  payload.forEach((item) => {
    values[item.name] = item.value;
  });

  const states = {
    1: "🔴 Bad",
    2: "🟠 Poor",
    3: "🟡 Okay",
    4: "🟢 Good",
    5: "⭐ Excellent"
  };

  return (
    <div className="custom-tooltip">

      <p className="tooltip-time">
        {new Date(label).toLocaleDateString()}{" "}
        {new Date(label).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        })}
    </p>

      <table>
        <tbody>

          {values.Temperature && (
            <tr>
              <td>Temperature</td>
              <td>{values.Temperature} °C</td>
            </tr>
          )}

          {values.Humidity && (
            <tr>
              <td>Humidity</td>
              <td>{values.Humidity} %</td>
            </tr>
          )}

          {values["CO₂"] && (
            <tr>
              <td>CO₂</td>
              <td>{values["CO₂"]} ppm</td>
            </tr>
          )}

          {values.Light && (
            <tr>
              <td>Light</td>
              <td>{values.Light} lx</td>
            </tr>
          )}

        </tbody>
      </table>

      <hr />

      <p>
        <strong>State:</strong>{" "}
        {states[values.State]}
      </p>

    </div>
  );
}