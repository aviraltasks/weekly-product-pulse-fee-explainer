"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AdminReviewStatus } from "@/components/AdminReviewStatus";
import { apiBase, readApiError } from "@/lib/api";
import type {
  PreviewCreateResponse,
  SubscriberRecord,
} from "@/lib/types";

function initSelection(rows: SubscriberRecord[]): Record<string, boolean> {
  const m: Record<string, boolean> = {};
  for (const r of rows) m[r.email] = true;
  return m;
}

type ReviewsStatusJson = { last_success_at_iso?: string | null };

function formatIst(iso: string | null | undefined): string {
  if (!iso) return "—";
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return "—";
  const s = new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(dt);
  return `${s} IST`;
}

export function AdminPreviewConsole() {
  const [preview, setPreview] = useState<PreviewCreateResponse | null>(null);
  const [subscribers, setSubscribers] = useState<SubscriberRecord[]>([]);
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [loadingSubs, setLoadingSubs] = useState(true);
  const [appendBusy, setAppendBusy] = useState(false);
  const [sendBusy, setSendBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [showJson, setShowJson] = useState(false);
  const [lastReviewFetchIso, setLastReviewFetchIso] = useState<string | null>(null);

  const loadSubscribers = useCallback(async () => {
    setError(null);
    const res = await fetch(`${apiBase()}/api/subscribers`, { cache: "no-store" });
    if (!res.ok) {
      throw new Error(await readApiError(res));
    }
    const data = (await res.json()) as { subscribers: SubscriberRecord[] };
    setSubscribers(data.subscribers);
    setSelected(initSelection(data.subscribers));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoadingSubs(true);
    loadSubscribers()
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : String(e));
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingSubs(false);
      });
    return () => {
      cancelled = true;
    };
  }, [loadSubscribers]);

  useEffect(() => {
    let cancelled = false;
    fetch(`${apiBase()}/api/reviews/status`, { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : Promise.resolve({})))
      .then((j: ReviewsStatusJson) => {
        if (!cancelled) setLastReviewFetchIso(j.last_success_at_iso ?? null);
      })
      .catch(() => {
        if (!cancelled) setLastReviewFetchIso(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const selectedEmails = useMemo(
    () => subscribers.filter((s) => selected[s.email]).map((s) => s.email),
    [subscribers, selected]
  );

  const onCreatePreview = async () => {
    setLoadingPreview(true);
    setError(null);
    setActionMessage(null);
    try {
      const res = await fetch(`${apiBase()}/api/preview/create`, {
        method: "POST",
      });
      if (!res.ok) {
        throw new Error(await readApiError(res));
      }
      const data = (await res.json()) as PreviewCreateResponse;
      setPreview(data);
      setActionMessage("Preview created. Review below, then append and/or send.");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoadingPreview(false);
    }
  };

  const onAppendDoc = async () => {
    if (!preview?.doc_block_plain) return;
    setAppendBusy(true);
    setError(null);
    setActionMessage(null);
    try {
      const res = await fetch(
        `${apiBase()}/api/integrations/google-doc/append`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            doc_block_plain: preview.doc_block_plain,
          }),
        }
      );
      if (!res.ok) {
        throw new Error(await readApiError(res));
      }
      const data = (await res.json()) as { document_url: string; inserted_char_count: number };
      setActionMessage(
        `Appended to Google Doc (${data.inserted_char_count} chars). Open: ${data.document_url}`
      );
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setAppendBusy(false);
    }
  };

  const onSendEmail = async () => {
    if (!preview) return;
    if (selectedEmails.length === 0) {
      setError("Select at least one subscriber email to send.");
      return;
    }
    setSendBusy(true);
    setError(null);
    setActionMessage(null);
    try {
      const res = await fetch(`${apiBase()}/api/integrations/gmail/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          to_emails: selectedEmails,
          subject: preview.email.subject,
          body_plain: preview.email.body_plain,
          body_html: preview.email.body_html,
        }),
      });
      if (!res.ok) {
        throw new Error(await readApiError(res));
      }
      const data = (await res.json()) as { sent_to: string[]; rejected: string[] };
      const rej =
        data.rejected?.length > 0
          ? ` Rejected (not in list): ${data.rejected.join(", ")}.`
          : "";
      setActionMessage(`Email sent to: ${data.sent_to.join(", ")}.${rej}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSendBusy(false);
    }
  };

  const toggleAll = (checked: boolean) => {
    const next: Record<string, boolean> = {};
    for (const s of subscribers) next[s.email] = checked;
    setSelected(next);
  };

  return (
    <div className="admin-console">
      
      <div className="admin-console__grid admin-console__grid--top">
        <AdminReviewStatus />
        <section className="card card--generate-preview" aria-label="Generate preview">
          <h2 className="font-serif card__title">Generate Preview</h2>
          <p className="muted">
            Runs the pulse pipeline (LLMs) and assigns the next Weekly Pulse serial. Use the
            result for Doc append and email — nothing sends automatically.
          </p>
          <button
            type="button"
            className="btn btn--primary"
            onClick={onCreatePreview}
            disabled={loadingPreview}
          >
            {loadingPreview ? "Creating preview…" : "Create preview"}
          </button>
        </section>
      </div>

      <div className="admin-console__grid">
        <section className="card" aria-label="Email recipients">
          <h2 className="font-serif card__title">Send to</h2>
          {loadingSubs && <p className="muted">Loading subscribers…</p>}
          {!loadingSubs && subscribers.length === 0 && (
            <p className="muted">
              No subscribers yet. Add emails on the Subscribers page first.
            </p>
          )}
          {!loadingSubs && subscribers.length > 0 && (
            <>
              <p className="muted small">
                Checked addresses receive email when you click Send email. Doc append does not
                use this list.
              </p>
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={selectedEmails.length === subscribers.length}
                  onChange={(e) => toggleAll(e.target.checked)}
                />
                <span>Select all</span>
              </label>
              <ul className="subscriber-list">
                {subscribers.map((s) => (
                  <li key={s.email}>
                    <label className="checkbox-row">
                      <input
                        type="checkbox"
                        checked={!!selected[s.email]}
                        onChange={(e) =>
                          setSelected((prev) => ({
                            ...prev,
                            [s.email]: e.target.checked,
                          }))
                        }
                      />
                      <span>{s.email}</span>
                    </label>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>

        <section className="card" aria-label="Actions">
          <h2 className="font-serif card__title">Integrations</h2>
          <p className="muted small">
            Append and Send are independent — use either or both after reviewing the preview.
          </p>
          <div className="stack">
            <button
              type="button"
              className="btn btn--dark"
              onClick={onAppendDoc}
              disabled={!preview || appendBusy}
            >
              {appendBusy ? "Appending…" : "Append to Google Doc"}
            </button>
            <button
              type="button"
              className="btn btn--dark"
              onClick={onSendEmail}
              disabled={!preview || sendBusy || subscribers.length === 0}
            >
              {sendBusy ? "Sending…" : "Send email"}
            </button>
          </div>
        </section>
      </div>

      {error && (
        <p className="alert alert--error" role="alert">
          {error}
        </p>
      )}
      {actionMessage && (
        <p className="alert alert--ok" role="status">
          {actionMessage}
        </p>
      )}

      {preview && (
        <section
          className="card preview-pane preview-pane--weekly"
          aria-label="Weekly Pulse preview content"
        >
          <div className="preview-pane__header">
            <div className="preview-pane__title-row">
              <h2 className="font-serif card__title preview-pane__title">
                Weekly Pulse {preview.weekly_pulse_n}
                <span className="preview-badge" title="Draft preview — not sent until you send email">
                  Preview
                </span>
              </h2>
            </div>
            <p className="muted small">
              As on — {preview.as_on.display}
            </p>
            <p className="muted small">Review Fetched On — {formatIst(lastReviewFetchIso)}</p>
            <button
              type="button"
              className="link-button"
              onClick={() => setShowJson((v) => !v)}
            >
              {showJson ? "Hide raw JSON" : "Show raw JSON"}
            </button>
          </div>

          {showJson && (
            <pre className="preview-json">{JSON.stringify(preview, null, 2)}</pre>
          )}

          <div className="preview-sections">
            <article>
              <h3 className="font-serif">Reviews&apos; themes (top 3)</h3>
              <ol>
                {preview.pulse.analysis.top_3_theme_names.map((name) => (
                  <li key={name}>{name}</li>
                ))}
              </ol>
            </article>
            <article>
              <h3 className="font-serif">Customer quotes:</h3>
              <ul>
                {preview.pulse.analysis.quotes.map((q) => (
                  <li key={`${q.theme}-${q.quote.slice(0, 24)}`}>
                    <strong>{q.theme}:</strong>{" "}
                    <em>&quot;{q.quote}&quot;</em>
                  </li>
                ))}
              </ul>
            </article>
            <article>
              <h3 className="font-serif">Weekly analysis:</h3>
              <p className="preview-note">{preview.pulse.weekly_note}</p>
            </article>
            <article>
              <h3 className="font-serif">Key takeaways/actionables:</h3>
              <ul>
                {preview.pulse.actions.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
            </article>
            {preview.pulse.fee && (
              <article>
                <h3 className="font-serif">This Week&apos;s Fee Explainer:</h3>
                <p>{preview.pulse.fee.fee_scenario}</p>
                <ul>
                  {preview.pulse.fee.explanation_bullets.map((b) => (
                    <li key={b}>{b}</li>
                  ))}
                </ul>
                <p className="small muted">
                  Sources:{" "}
                  {preview.pulse.fee.source_links.map((u, i) => (
                    <span key={u}>
                      {i > 0 ? " · " : ""}
                      <a href={u} target="_blank" rel="noopener noreferrer">
                        {u}
                      </a>
                    </span>
                  ))}
                </p>
              </article>
            )}
          </div>

          <details className="email-preview-details" open>
            <summary>Email subject & preview (HTML — same as sent)</summary>
            <p>
              <strong>Subject:</strong> {preview.email.subject}
            </p>
            <div className="email-html-preview-wrap">
              <iframe
                title="Email HTML preview (matches sent mail)"
                className="email-html-frame"
                key={`email-html-${preview.weekly_pulse_n}-${preview.as_on.iso_utc}-${preview.email.format_version ?? "x"}`}
                srcDoc={preview.email.body_html}
                sandbox="allow-same-origin"
              />
            </div>
            <details className="email-plain-subdetails">
              <summary>Plain-text version (fallback for text-only clients)</summary>
              <pre className="email-plain">{preview.email.body_plain}</pre>
            </details>
          </details>
        </section>
      )}
    </div>
  );
}
