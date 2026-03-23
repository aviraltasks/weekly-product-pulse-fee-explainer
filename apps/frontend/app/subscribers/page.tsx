import Link from "next/link";
import { SubscribeForm } from "@/components/SubscribeForm";

export default function SubscribersPage() {
  return (
    <>
      <Link href="/" className="back-link">
        ← Home
      </Link>
      <h1 className="font-serif" style={{ fontSize: "clamp(1.75rem, 4vw, 2.25rem)" }}>
        Subscribers
      </h1>
      <p className="muted" style={{ marginBottom: "2rem", maxWidth: "36ch" }}>
        Enter your work email to join the list. The admin selects recipients when sending;
        nothing is mailed automatically.
      </p>
      <SubscribeForm />
    </>
  );
}
