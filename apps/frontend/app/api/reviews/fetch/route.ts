import { NextResponse } from "next/server";

function backendApiBase(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

export async function POST() {
  const token = (process.env.CRON_TRIGGER_TOKEN || "").trim();
  if (!token) {
    return NextResponse.json(
      { detail: "Server misconfigured: CRON_TRIGGER_TOKEN is not set." },
      { status: 503 }
    );
  }

  const upstream = await fetch(`${backendApiBase()}/api/reviews/fetch`, {
    method: "POST",
    headers: {
      "X-Cron-Token": token,
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  let payload: unknown;
  try {
    payload = await upstream.json();
  } catch {
    payload = { detail: upstream.statusText || `HTTP ${upstream.status}` };
  }
  return NextResponse.json(payload, { status: upstream.status });
}

