"use client";

import { useCallback, useEffect, useState } from "react";

const apiBase = () =>
  (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
    /\/$/,
    ""
  );

/** Human-readable UTC (no raw ISO in the UI). */
export function formatUtcInstant(iso: string | null): string {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return (
      new Intl.DateTimeFormat("en-GB", {
        dateStyle: "medium",
        timeStyle: "short",
        timeZone: "UTC",
      }).format(d) + " UTC"
    );
  } catch {
    return iso;
  }
}

export type ReviewsStatus = {
  review_count: number;
  last_attempt_at_iso: string | null;
  last_success_at_iso: string | null;
  last_error: string | null;
  last_added_count: number;
  play_store_app_id: string;
  scheduler_enabled: boolean;
  fetch_interval_hours: number;
};

export function AdminReviewStatus() {
  const [status, setStatus] = useState<ReviewsStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadStatus = useCallback(async () => {
    setError(null);
    const res = await fetch(`${apiBase()}/api/reviews/status`, { cache: "no-store" });
    if (!res.ok) {
      throw new Error(`Status ${res.status}`);
    }
    const data = (await res.json()) as ReviewsStatus;
    setStatus(data);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loadStatus()
      .catch((e: unknown) => {
        if (!cancelled) {
          const raw = e instanceof Error ? e.message : String(e);
          setError(friendlyErrorMessage(raw));
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [loadStatus]);

  const onRefreshReviews = async () => {
    setRefreshing(true);
    setError(null);
    try {
      // Safe server-side proxy; token stays in frontend server env (not exposed to browser).
      const res = await fetch(`/api/reviews/fetch`, {
        method: "POST",
      });
      if (!res.ok) {
        throw new Error(`Fetch failed: ${res.status}`);
      }
      await loadStatus();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <section
      aria-label="Reviews refresh status"
      className="card card--reviews-data"
      data-testid="admin-review-status"
    >
      <h2 className="font-serif card__title">Reviews data</h2>
      {loading && <p className="muted">Loading status…</p>}
      {error && (
        <p role="alert" className="alert alert--error">
          {error}
        </p>
      )}
      {status && !loading && (
        <dl className="reviews-stats">
          <div className="reviews-stats__row">
            <dt>Reviews in CSV</dt>
            <dd>{status.review_count}</dd>
          </div>
          <div className="reviews-stats__row">
            <dt>Play Store app id</dt>
            <dd>
              <code className="reviews-stats__code">{status.play_store_app_id}</code>
            </dd>
          </div>
          <div className="reviews-stats__row">
            <dt>Last success</dt>
            <dd>{formatUtcInstant(status.last_success_at_iso)}</dd>
          </div>
          <div className="reviews-stats__row">
            <dt>Last attempt</dt>
            <dd>{formatUtcInstant(status.last_attempt_at_iso)}</dd>
          </div>
          {status.last_error && (
            <div className="reviews-stats__row reviews-stats__row--error">
              <dt>Last error</dt>
              <dd>{status.last_error}</dd>
            </div>
          )}
          <div className="reviews-stats__row">
            <dt>Automated fetch</dt>
            <dd>
              {status.scheduler_enabled
                ? `In-app job every ${status.fetch_interval_hours}h (CSV only)`
                : "GitHub Actions cron every 48h (in-app scheduler disabled in production)"}
            </dd>
          </div>
        </dl>
      )}
      <p className="reviews-stats__actions">
        <button
          type="button"
          className="btn btn--muted"
          onClick={onRefreshReviews}
          disabled={refreshing || loading}
        >
          {refreshing ? "Fetching…" : "Refresh reviews now"}
        </button>
      </p>
    </section>
  );
}
