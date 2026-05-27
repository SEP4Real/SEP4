import { describe, test, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { LanguageProvider } from "../context/LanguageContext";
import LoginPage from "./LoginPage";
import { login } from "../services/AuthService";

vi.mock("../services/AuthService", () => ({
  login: vi.fn(),
}));

function renderLoginPage() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <LanguageProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<h1>Dashboard page</h1>} />
        </Routes>
      </LanguageProvider>
    </MemoryRouter>
  );
}

describe("Login auth flow", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  test("shows validation when email or password is missing", async () => {
    const user = userEvent.setup();

    renderLoginPage();

    await user.click(screen.getByRole("button", { name: /^login$/i }));

    expect(screen.getByText("Enter email and password")).toBeInTheDocument();
    expect(login).not.toHaveBeenCalled();
  });

  test("logs in, stores the user and navigates to dashboard", async () => {
    const user = userEvent.setup();
    const loggedInUser = {
      id: "user-1",
      name: "Cristina",
      email: "cristina@example.com",
    };

    login.mockResolvedValue({
      user: loggedInUser,
    });

    renderLoginPage();

    await user.type(screen.getByLabelText(/email/i), "cristina@example.com");
    await user.type(screen.getByLabelText(/^password:$/i), "secret123");
    await user.click(screen.getByRole("button", { name: /^login$/i }));

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith({
        email: "cristina@example.com",
        password: "secret123",
      });
      expect(screen.getByText("Dashboard page")).toBeInTheDocument();
    });

    expect(JSON.parse(localStorage.getItem("user"))).toEqual(loggedInUser);
  });
});
