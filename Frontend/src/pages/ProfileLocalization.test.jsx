import { describe, test, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LanguageProvider, useLanguage } from "../context/LanguageContext";

function TestProfileLocalization() {
  const { language, toggleLanguage, t } = useLanguage();

  return (
    <div>
      <p>{t.profile}</p>
      <p>{t.email}</p>
      <p>{t.password}</p>
      <span>{language}</span>

      <button onClick={toggleLanguage}>
        Switch language
      </button>
    </div>
  );
}

describe("Profile localization", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test("renders profile related texts in English by default", () => {
    render(
      <LanguageProvider>
        <TestProfileLocalization />
      </LanguageProvider>
    );

    expect(screen.getByText("Profile")).toBeInTheDocument();
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("Password")).toBeInTheDocument();
  });

  test("switches profile related texts to Danish", async () => {
    const user = userEvent.setup();

    render(
      <LanguageProvider>
        <TestProfileLocalization />
      </LanguageProvider>
    );

    await user.click(screen.getByRole("button", { name: /switch language/i }));

    expect(screen.getByText("Profil")).toBeInTheDocument();
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("Adgangskode")).toBeInTheDocument();
  });
});