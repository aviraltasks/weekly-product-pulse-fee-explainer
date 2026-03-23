import Link from "next/link";
import { AdminPreviewConsole } from "@/components/AdminPreviewConsole";

/** Avoid edge/CDN serving a stale admin shell; always get fresh HTML + JS after deploy. */
export const dynamic = "force-dynamic";

export default function AdminPage() {
  return (
    <>
      <Link href="/" className="back-link">
        ← Home
      </Link>
      <h1 className="font-serif" style={{ fontSize: "clamp(1.75rem, 4vw, 2.25rem)" }}>
        Admin
      </h1>
      <p className="muted" style={{ marginBottom: "1.5rem", maxWidth: "42ch" }}>
        Check review freshness, create a new preview (increments Weekly Pulse N), then
        append to the master Google Doc and/or send email to checked subscribers.
      </p>
      <AdminPreviewConsole />
    </>
  );
}
