import { describe, test, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LanguageProvider } from "../context/LanguageContext";
import Dashboard from "./Dashboard";
import { getDashboardData } from "../services/DashboardService";
import { getCurrentSession } from "../services/SessionService";
import { getProfile } from "../services/ProfileService";

vi.mock("../services/DashboardService", () => ({
  getDashboardData: vi.fn(),
}));

vi.mock("../services/SessionService", () => ({
  getCurrentSession: vi.fn(),
}));

vi.mock("../services/ProfileService", () => ({
  getProfile: vi.fn(),
}));

vi.mock("../components/SensorChart", () => ({
  default: () => <div>Sensor chart</div>,
}));

vi.mock("../components/SessionRating", () => ({
  default: ({ deviceId, sessionId }) => (
    <div>
      <p>Rating popup</p>
      <p>Device: {deviceId}</p>
      <p>Session: {sessionId}</p>
    </div>
  ),
}));

const dashboardRecord = {
  id: 1,
  temperature: 23,
  humidity: 45,
  co2_level: 700,
  light_level: 300,
  predicted_study_quality: 4,
  sent_at: "2026-05-24T12:00:00Z",
};

describe("Dashboard stop session flow", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();

    localStorage.setItem(
      "user",
      JSON.stringify({
        email: "cristina@example.com",
        name: "Cristina",
      })
    );

    getProfile.mockResolvedValue({
      profile: {
        connected_device_id: "arduino-device-01",
      },
    });
    getDashboardData.mockResolvedValue([dashboardRecord]);
    getCurrentSession.mockResolvedValue({
      id: 9,
      deviceId: "arduino-device-01",
      isEnded: false,
    });
  });

  test("opens rating popup with active session when Stop Session is clicked", async () => {
    const user = userEvent.setup();

    render(
      <LanguageProvider>
        <Dashboard />
      </LanguageProvider>
    );

    await user.click(
      await screen.findByRole("button", { name: /start session/i })
    );

    await waitFor(() => {
      expect(getCurrentSession).toHaveBeenCalledWith("arduino-device-01");
    });

    await user.click(screen.getByRole("button", { name: /stop session/i }));

    expect(screen.getByText("Rating popup")).toBeInTheDocument();
    expect(screen.getByText("Device: arduino-device-01")).toBeInTheDocument();
    expect(screen.getByText("Session: 9")).toBeInTheDocument();
  });
});
