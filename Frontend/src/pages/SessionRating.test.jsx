import { describe, test, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SessionRating from "../components/SessionRating";
import { LanguageProvider } from "../context/LanguageContext";

describe("SessionRating", () => {
  beforeEach(() => {
    localStorage.clear();

    globalThis.fetch = vi.fn(() =>
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

    await user.click(screen.getByRole("button", { name: /submit rating/i }));

    expect(
      screen.getByText("Please select a rating.")
    ).toBeInTheDocument();
  });

  test("submits selected rating and calls onSuccess", async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();

    render(
      <LanguageProvider>
        <SessionRating onSuccess={onSuccess} sessionId={1} />
      </LanguageProvider>
    );

    const buttons = screen.getAllByRole("button");

    await user.click(buttons[2]);
    await user.click(screen.getByRole("button", { name: /submit rating/i }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalled();
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  test("sends device id, session id and rating in the request body", async () => {
    const user = userEvent.setup();

    render(
      <LanguageProvider>
        <SessionRating
          deviceId="arduino-device-01"
          sessionId={12}
          onSuccess={vi.fn()}
        />
      </LanguageProvider>
    );

    const buttons = screen.getAllByRole("button");

    await user.click(buttons[4]);
    await user.click(screen.getByRole("button", { name: /submit rating/i }));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        "/api/ratings",
        expect.objectContaining({
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            device_id: "arduino-device-01",
            session_id: 12,
            rating: 5,
            comment: "",
          }),
        })
      );
    });
  });
});
