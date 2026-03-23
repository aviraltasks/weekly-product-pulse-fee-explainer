/**
 * Global footer — ARCHITECTURE.md §2.1
 * Loads full architecture text from /architecture-full.md.
 */
"use client";

import { useEffect, useState } from "react";
import { SITE_LAST_DEPLOYED, SITE_LAST_DEPLOYED_ISO } from "@/lib/siteMeta";

export function Footer() {
  const [architectureText, setArchitectureText] = useState("Loading architecture...");

  useEffect(() => {
    let cancelled = false;
    fetch("/architecture-full.md")
      .then((res) => (res.ok ? res.text() : Promise.resolve("Unable to load architecture file.")))
      .then((txt) => {
        if (!cancelled) setArchitectureText(txt);
      })
      .catch(() => {
        if (!cancelled) setArchitectureText("Unable to load architecture file.");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <footer className="app-footer">
      <p>
        Last deployed on{" "}
        <time dateTime={SITE_LAST_DEPLOYED_ISO}>{SITE_LAST_DEPLOYED}</time>
      </p>
      <p>
        <strong className="font-serif">Weekly Product Pulse and Fee Explainer</strong>
      </p>
      <p>Project created by Aviral Rawat</p>
      <p>
        <a
          href="https://www.linkedin.com/in/aviralrawat/"
          target="_blank"
          rel="noopener noreferrer"
        >
          LinkedIn
        </a>
      </p>
      <p>Built with Cursor</p>
      <div className="app-footer__accordion-wrap">
        <details className="app-footer__accordion">
          <summary>System Design (Architecture)</summary>
          <div className="details-body">
            <pre className="details-body__full">{architectureText}</pre>
          </div>
        </details>
      </div>
    </footer>
  );
}
