import Link from "next/link";

export default function HomePage() {
  return (
    <>
      <section className="hero">
        <div className="hero__text">
          <h1>Weekly pulse, clearly explained.</h1>
          <p className="lede">
            Turn Play Store signals into a structured leadership summary and a consistent
            Exit Load explainer — then push to your doc and subscribers when you choose.
          </p>
        </div>
        <div className="hero__visual" aria-hidden>
          <div className="hero__glass-card">
            <div className="hero__metrics-row">
              <span className="hero__metric hero__metric--lg" />
              <span className="hero__metric hero__metric--md" />
              <span className="hero__metric hero__metric--sm" />
            </div>
            <div className="hero__bars">
              <span className="hero__bar hero__bar--a" />
              <span className="hero__bar hero__bar--b" />
              <span className="hero__bar hero__bar--c" />
              <span className="hero__bar hero__bar--d" />
            </div>
            <div className="hero__rating-row">
              <span className="hero__dot" />
              <span className="hero__dot" />
              <span className="hero__dot" />
              <span className="hero__dot" />
              <span className="hero__dot hero__dot--muted" />
            </div>
            <div className="hero__sparkline" />
            <div className="hero__visual-label">Signal Overview</div>
          </div>
        </div>
      </section>

      <section className="entry-cards" aria-label="Entry points">
        <article className="entry-card">
          <h2>Subscribers</h2>
          <p>
            Add your email so the admin can include you when sending the weekly pulse
            newsletter.
          </p>
          <Link href="/subscribers" className="entry-card__cta">
            <span>Subscribers Enter</span>
            <span className="arrow" aria-hidden>
              ↗
            </span>
          </Link>
        </article>
        <article className="entry-card">
          <h2>Admin</h2>
          <p>
            Refresh reviews, create a preview, append to Google Doc, and send email to
            selected subscribers.
          </p>
          <Link href="/admin" className="entry-card__cta">
            <span>Admin Enter</span>
            <span className="arrow" aria-hidden>
              ↗
            </span>
          </Link>
        </article>
      </section>
    </>
  );
}
