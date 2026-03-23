"use client";

import { FormEvent, useState } from "react";
import { apiBase, readApiError } from "@/lib/api";

export function SubscribeForm() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "err">("idle");
  const [message, setMessage] = useState<string | null>(null);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setStatus("loading");
    setMessage(null);
    try {
      const res = await fetch(`${apiBase()}/api/subscribers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) {
        throw new Error(await readApiError(res));
      }
      setStatus("ok");
      setMessage("You’re subscribed. The admin can include you when sending the weekly email.");
      setEmail("");
    } catch (err: unknown) {
      setStatus("err");
      setMessage(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <form className="subscribe-form" onSubmit={onSubmit}>
      <label htmlFor="sub-email" className="sr-only">
        Email
      </label>
      <input
        id="sub-email"
        name="email"
        type="email"
        required
        autoComplete="email"
        placeholder="you@company.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        disabled={status === "loading"}
        className="input"
      />
      <button
        type="submit"
        className="btn btn--dark"
        disabled={status === "loading"}
      >
        {status === "loading" ? "Submitting…" : "Subscribe"}
      </button>
      {message && (
        <p
          className={status === "ok" ? "alert alert--ok" : "alert alert--error"}
          role="status"
        >
          {message}
        </p>
      )}
    </form>
  );
}
