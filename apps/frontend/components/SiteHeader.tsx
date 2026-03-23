"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  { href: "/", label: "Home" },
  { href: "/subscribers", label: "Subscribers" },
  { href: "/admin", label: "Admin" },
];

/** Static shell while `usePathname` resolves (see root `layout` + Suspense). */
export function SiteHeaderFallback() {
  return (
    <header className="site-header">
      <div className="site-header__inner">
        <Link href="/" className="site-logo font-serif">
          INDmoney Feedback Pulse
        </Link>
        <nav className="site-nav" aria-label="Primary">
          {nav.map(({ href, label }) => (
            <Link key={href} href={href} className="site-nav__link">
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <Link href="/" className="site-logo font-serif">
          INDmoney Feedback Pulse
        </Link>
        <nav className="site-nav" aria-label="Primary">
          {nav.map(({ href, label }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`site-nav__link${active ? " site-nav__link--active" : ""}`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
