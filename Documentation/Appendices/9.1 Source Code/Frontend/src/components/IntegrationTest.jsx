import { useState } from "react";
import { getIoTHealthCheck } from "../services/iotService";
import { getMalHealthCheck } from "../services/malService";

export default function IntegrationTest() {
  const [iotStatus, setIotStatus] = useState("Not checked");
  const [malStatus, setMalStatus] = useState("Not checked");

  async function checkIoT() {
    try {
      const data = await getIoTHealthCheck();
      setIotStatus(JSON.stringify(data));
    } catch (error) {
      setIotStatus(error.message);
    }
  }

  async function checkMal() {
    try {
      const data = await getMalHealthCheck();
      setMalStatus(JSON.stringify(data));
    } catch (error) {
      setMalStatus(error.message);
    }
  }

  return (
    <div style={{ padding: "120px 40px" }}>
      <h1>Backend Integration Test</h1>

      <section>
        <h2>IoT Backend</h2>
        <button onClick={checkIoT}>Check IoT Backend</button>
        <p>{iotStatus}</p>
      </section>

      <section>
        <h2>MAL Backend</h2>
        <button onClick={checkMal}>Check MAL Backend</button>
        <p>{malStatus}</p>
      </section>
    </div>
  );
}