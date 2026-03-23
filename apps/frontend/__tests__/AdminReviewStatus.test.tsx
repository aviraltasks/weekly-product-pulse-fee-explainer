import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AdminReviewStatus } from "@/components/AdminReviewStatus";

describe("AdminReviewStatus", () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it("loads and shows review count from /api/reviews/status", async () => {
    global.fetch = jest.fn().mockImplementation((url: string | URL) => {
      const u = String(url);
      if (u.endsWith("/api/reviews/status")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            review_count: 42,
            last_attempt_at_iso: null,
            last_success_at_iso: "2025-01-01T00:00:00+00:00",
            last_error: null,
            last_added_count: 0,
            play_store_app_id: "in.test",
            scheduler_enabled: true,
            fetch_interval_hours: 48,
          }),
        });
      }
      return Promise.reject(new Error("unexpected url " + u));
    }) as jest.Mock;

    render(<AdminReviewStatus />);

    await waitFor(() => {
      expect(screen.getByText(/Reviews in CSV/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/42/)).toBeInTheDocument();
    expect(screen.getByText(/in\.test/)).toBeInTheDocument();
  });

  it("POST /api/reviews/fetch then reloads status", async () => {
    const user = userEvent.setup();
    let statusCalls = 0;
    global.fetch = jest.fn().mockImplementation((url: string | URL, init) => {
      const u = String(url);
      if (u.endsWith("/api/reviews/status")) {
        statusCalls += 1;
        return Promise.resolve({
          ok: true,
          json: async () => ({
            review_count: statusCalls === 1 ? 0 : 3,
            last_attempt_at_iso: null,
            last_success_at_iso: "2025-01-02T00:00:00+00:00",
            last_error: null,
            last_added_count: statusCalls === 1 ? 0 : 3,
            play_store_app_id: "in.test",
            scheduler_enabled: true,
            fetch_interval_hours: 48,
          }),
        });
      }
      if (u.endsWith("/api/reviews/fetch") && init?.method === "POST") {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            ok: true,
            review_count: 3,
            last_success_at_iso: "2025-01-02T00:00:00+00:00",
            last_error: null,
            last_added_count: 3,
          }),
        });
      }
      return Promise.reject(new Error("unexpected " + u));
    }) as jest.Mock;

    render(<AdminReviewStatus />);

    await waitFor(() => {
      expect(screen.getByText(/Reviews in CSV/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/^0$/)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Refresh reviews now/i }));

    await waitFor(() => {
      expect(screen.getByText(/^3$/)).toBeInTheDocument();
    });
  });
});
