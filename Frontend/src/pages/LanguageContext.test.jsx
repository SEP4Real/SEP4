/* eslint-env vitest */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LanguageProvider, useLanguage } from "../context/LanguageContext";
function TestLanguageComponent() {
  const { language, toggleLanguage, t } = useLanguage();

  return (
    <div>
      <p>Current language: {language}</p>
     <p>{t.home}</p>

      <button onClick={toggleLanguage}>
        Switch language
      </button>
    </div>
  );
}

describe("LanguageContext", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test("uses English as default language", () => {
    render(
      <LanguageProvider>
        <TestLanguageComponent />
      </LanguageProvider>
    );

    expect(screen.getByText("Current language: en")).toBeInTheDocument();
expect(screen.getByText("Home")).toBeInTheDocument();  });

  test("switches language from English to Danish", async () => {
    const user = userEvent.setup();

    render(
      <LanguageProvider>
        <TestLanguageComponent />
      </LanguageProvider>
    );

    await user.click(screen.getByRole("button", { name: /switch language/i }));

    expect(screen.getByText("Current language: da")).toBeInTheDocument();
expect(screen.getByText("Hjem")).toBeInTheDocument();  });

  test("saves selected language to localStorage", async () => {
    const user = userEvent.setup();

    render(
      <LanguageProvider>
        <TestLanguageComponent />
      </LanguageProvider>
    );

    await user.click(screen.getByRole("button", { name: /switch language/i }));

    expect(localStorage.getItem("language")).toBe("da");
  });
});