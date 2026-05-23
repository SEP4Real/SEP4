import { render, screen } from "@testing-library/react";
import EmptyState from "../components/EmptyState";
import LoadingSpinner from "../components/LoadingSpinner";

describe("Dashboard UI states", () => {
  test("renders empty state message", () => {
    render(
      <EmptyState
        icon="📡"
        title="No device connected"
        message="Go to Profile to connect your device."
      />
    );

    expect(screen.getByText("No device connected")).toBeInTheDocument();
    expect(
      screen.getByText("Go to Profile to connect your device.")
    ).toBeInTheDocument();
  });

  test("renders loading spinner text", () => {
    render(<LoadingSpinner text="Loading environment data..." />);

    expect(
      screen.getByText("Loading environment data...")
    ).toBeInTheDocument();

    expect(screen.getByText("⏳")).toBeInTheDocument();
  });
});