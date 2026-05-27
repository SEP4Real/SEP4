import { describe, test, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { LanguageProvider } from "../context/LanguageContext";
import Profile from "./Profile";
import { ensureDeviceExists } from "../services/DeviceService";
import { getProfile, updateProfile } from "../services/ProfileService";

vi.mock("../services/DeviceService", () => ({
  ensureDeviceExists: vi.fn(),
}));

vi.mock("../services/ProfileService", () => ({
  getProfile: vi.fn(),
  updatePassword: vi.fn(),
  updateProfile: vi.fn(),
}));

vi.mock("../services/AuthService", () => ({
  logout: vi.fn(),
}));

const loggedInUser = {
  id: "user-1",
  name: "Cristina",
  last_name: "Test",
  email: "cristina@example.com",
};

function renderProfile() {
  return render(
    <MemoryRouter>
      <LanguageProvider>
        <Profile />
      </LanguageProvider>
    </MemoryRouter>
  );
}

describe("Profile connected device", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(window, "alert").mockImplementation(() => {});

    localStorage.setItem("user", JSON.stringify(loggedInUser));

    getProfile.mockResolvedValue({
      user: loggedInUser,
      profile: {
        university: "",
        study_program: "",
        study_year: "",
        study_goal: "",
        preferred_temp: 22,
        preferred_co2: 800,
        connected_device_id: "",
        profile_picture: null,
      },
    });

    ensureDeviceExists.mockResolvedValue({ id: "arduino-device-01" });
    updateProfile.mockResolvedValue({ message: "Profile updated successfully" });
  });

  test("shows the connected device saved in the backend profile", async () => {
    getProfile.mockResolvedValueOnce({
      user: loggedInUser,
      profile: {
        connected_device_id: "arduino-device-01",
      },
    });

    renderProfile();

    expect(await screen.findByText("arduino-device-01")).toBeInTheDocument();
  });

  test("saves the connected device id in the user profile", async () => {
    const user = userEvent.setup();

    renderProfile();

    const deviceInput = await screen.findByDisplayValue("arduino-device-01");

    await user.clear(deviceInput);
    await user.type(deviceInput, "arduino-device-01");
    await user.click(screen.getByRole("button", { name: /connect now/i }));

    await waitFor(() => {
      expect(ensureDeviceExists).toHaveBeenCalledWith("arduino-device-01");
      expect(updateProfile).toHaveBeenCalledWith(
        expect.objectContaining({
          connected_device_id: "arduino-device-01",
        })
      );
    });
  });
});
