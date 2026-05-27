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

vi.mock("../components/SensorCard", () => ({
  default: ({ title, value }) => (
    <div>
      <span>{title}</span>
      <strong>{value}</strong>
    </div>
  ),
}));

vi.mock("../components/SessionRating", () => ({
  default: () => <div>Session rating</div>,
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

function renderDashboard() {
  return render(
    <LanguageProvider>
      <Dashboard />
    </LanguageProvider>
  );
}

describe("Dashboard session flow", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();

    localStorage.setItem(
      "user",
      JSON.stringify({
        id: "user-1",
        name: "Cristina",
        email: "cristina@example.com",
      })
    );

    getProfile.mockResolvedValue({
      profile: {
        connected_device_id: "arduino-device-01",
      },
    });

    getDashboardData.mockResolvedValue([dashboardRecord]);
  });

  test("keeps live data locked when no active backend session exists", async () => {
    const user = userEvent.setup();
    getCurrentSession.mockResolvedValue(null);

    renderDashboard();

    await user.click(
      await screen.findByRole("button", { name: /start session/i })
    );

    expect(getCurrentSession).toHaveBeenCalledWith("arduino-device-01");
    expect(
      await screen.findByText(
        "No active session found. Make sure the device is running."
      )
    ).toBeInTheDocument();
    expect(screen.queryByText("Temperature")).not.toBeInTheDocument();
  });

  test("unlocks live data when an active backend session exists", async () => {
    const user = userEvent.setup();
    getCurrentSession.mockResolvedValue({
      id: 3,
      deviceId: "arduino-device-01",
      isEnded: false,
    });

    renderDashboard();

    await user.click(
      await screen.findByRole("button", { name: /start session/i })
    );

    expect(getCurrentSession).toHaveBeenCalledWith("arduino-device-01");
    expect(await screen.findByText("Temperature")).toBeInTheDocument();
    expect(screen.getByText("Sensor chart")).toBeInTheDocument();
  });
});
