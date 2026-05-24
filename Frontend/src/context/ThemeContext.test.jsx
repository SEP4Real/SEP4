import { describe, test, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ThemeProvider, useTheme } from "./ThemeContext";

function TestThemeComponent() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div>
      <p>Current theme: {theme}</p>

      <button onClick={toggleTheme}>
        Switch theme
      </button>
    </div>
  );
}

describe("ThemeContext", () => {
  beforeEach(() => {
    localStorage.clear();

    document.body.classList.remove("light-theme");
    document.body.classList.remove("dark-theme");
  });

  test("uses light theme as default", () => {
    render(
      <ThemeProvider>
        <TestThemeComponent />
      </ThemeProvider>
    );

    expect(screen.getByText("Current theme: light")).toBeInTheDocument();
    expect(document.body.classList.contains("light-theme")).toBe(true);
  });

  test("switches theme from light to dark", async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider>
        <TestThemeComponent />
      </ThemeProvider>
    );

    await user.click(screen.getByRole("button", { name: /switch theme/i }));

    expect(screen.getByText("Current theme: dark")).toBeInTheDocument();
    expect(document.body.classList.contains("dark-theme")).toBe(true);
  });

  test("saves selected theme to localStorage", async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider>
        <TestThemeComponent />
      </ThemeProvider>
    );

    await user.click(screen.getByRole("button", { name: /switch theme/i }));

    expect(localStorage.getItem("theme")).toBe("dark");
  });
});