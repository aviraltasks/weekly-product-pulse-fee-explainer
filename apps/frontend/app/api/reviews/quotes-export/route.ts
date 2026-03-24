import { NextResponse } from "next/server";

function backendApiBase(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

/** Proxy CSV export so the admin link is same-origin (reliable download + no CORS). */
export async function GET() {
  const upstream = await fetch(`${backendApiBase()}/api/reviews/quotes-export`, {
    cache: "no-store",
  });

  if (!upstream.ok) {
    const text = await upstream.text();
    return new NextResponse(text, {
      status: upstream.status,
      headers: {
        "Content-Type":
          upstream.headers.get("content-type") || "application/json",
        "Cache-Control": "no-store",
      },
    });
  }

  const buf = await upstream.arrayBuffer();
  const headers = new Headers();
  const ct = upstream.headers.get("content-type") || "text/csv; charset=utf-8";
  headers.set("Content-Type", ct);
  const cd = upstream.headers.get("content-disposition");
  if (cd) {
    headers.set("Content-Disposition", cd);
  }
  headers.set("Cache-Control", "no-store");

  return new NextResponse(buf, { status: 200, headers });
}
