import { describe, test, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";
import { LanguageProvider } from "./context/LanguageContext";
import { ThemeProvider } from "./context/ThemeContext";

vi.mock("./pages/LoginPage", () => ({
  default: () => <h1>Login Page</h1>,
}));

vi.mock("./pages/RegisterPage", () => ({
  default: () => <h1>Register Page</h1>,
}));

vi.mock("./pages/Dashboard", () => ({
  default: () => <h1>Dashboard Page</h1>,
}));

vi.mock("./pages/Profile", () => ({
  default: () => <h1>Profile Page</h1>,
}));

vi.mock("./pages/CalendarPage", () => ({
  default: () => <h1>Calendar Page</h1>,
}));

function renderAppAt(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <ThemeProvider>
        <LanguageProvider>
          <App />
        </LanguageProvider>
      </ThemeProvider>
    </MemoryRouter>
  );
}

describe("Production routing smoke test", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test("renders the login page from a direct login URL", () => {
    renderAppAt("/login");

    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  test("renders the dashboard from a direct dashboard URL when logged in", () => {
    localStorage.setItem(
      "user",
      JSON.stringify({
        id: "user-1",
        name: "Cristina",
        email: "cristina@example.com",
      })
    );

    renderAppAt("/dashboard");

    expect(screen.getByText("Dashboard Page")).toBeInTheDocument();
  });

  test("redirects unknown direct URLs to the dashboard for logged in users", () => {
    localStorage.setItem(
      "user",
      JSON.stringify({
        id: "user-1",
        name: "Cristina",
        email: "cristina@example.com",
      })
    );

    renderAppAt("/not-a-real-page");

    expect(screen.getByText("Dashboard Page")).toBeInTheDocument();
  });
});
