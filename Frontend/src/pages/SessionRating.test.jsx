/* eslint-env vitest */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import SessionRating from "../components/SessionRating";
import { LanguageProvider } from "../context/LanguageContext";

describe("SessionRating", () => {
  beforeEach(() => {
    localStorage.clear();

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      })
    );
  });

  test("renders session rating title and rating buttons", () => {
    render(
      <LanguageProvider>
        <SessionRating onSuccess={vi.fn()} />
      </LanguageProvider>
    );

    expect(
      screen.getByText("How was your study session?")
    ).toBeInTheDocument();

    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThanOrEqual(5);
  });

  test("shows validation message when no rating is selected", async () => {
    const user = userEvent.setup();

    render(
      <LanguageProvider>
        <SessionRating onSuccess={vi.fn()} />
      </LanguageProvider>
    );

    await user.click(screen.getByRole("button", { name: /submit & logout/i }));

    expect(
      screen.getByText("Please select a rating.")
    ).toBeInTheDocument();
  });

  test("submits selected rating and calls onSuccess", async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();

    render(
      <LanguageProvider>
        <SessionRating onSuccess={onSuccess} />
      </LanguageProvider>
    );

    const buttons = screen.getAllByRole("button");

    await user.click(buttons[2]);
    await user.click(screen.getByRole("button", { name: /submit & logout/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
      expect(onSuccess).toHaveBeenCalled();
    });
  });
});