"use client";

import { FormEvent, useMemo, useState } from "react";
import { ApiError, parseValidationDetail, postRecommendations } from "@/lib/api";
import type { RecommendationResponse } from "@/lib/types";

const inputClass =
  "mt-1.5 w-full rounded-xl border border-zinc-200 bg-white px-3.5 py-2.5 text-sm text-ink shadow-sm transition placeholder:text-ink-secondary/70 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20";

const labelClass = "block text-sm font-semibold text-ink";

function ExperienceBanner({ experience, degraded }: { experience: string | null | undefined; degraded: boolean }) {
  const exp = experience ?? "ok";
  if (exp === "empty") {
    return (
      <div
        role="status"
        className="rounded-card border border-amber-200 bg-amber-50/90 px-4 py-3 text-sm text-amber-950 shadow-sm"
      >
        <strong>No matches</strong> — try relaxing location, budget, cuisines, or minimum rating.
      </div>
    );
  }
  if (degraded || exp === "degraded") {
    return (
      <div
        role="status"
        className="rounded-card border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950 shadow-sm"
      >
        <strong>Degraded mode</strong> — rankings use a deterministic fallback; explanations may be shorter.
      </div>
    );
  }
  if (exp === "ok") {
    return (
      <div
        role="status"
        className="rounded-card border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-950 shadow-sm"
      >
        <strong>Results ready</strong> — picks loaded for your preferences.
      </div>
    );
  }
  return null;
}

export default function Home() {
  const [location, setLocation] = useState("Bangalore");
  const [budget, setBudget] = useState("medium");
  const [cuisinesRaw, setCuisinesRaw] = useState("Chinese, North Indian");
  const [minRating, setMinRating] = useState(4);
  const [notes, setNotes] = useState("");
  const [limit, setLimit] = useState(5);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<RecommendationResponse | null>(null);
  const [clientError, setClientError] = useState<string | null>(null);
  const [validationMsg, setValidationMsg] = useState<string | null>(null);

  const apiBaseDisplay = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000",
    [],
  );

  const cuisineChips = useMemo(
    () =>
      cuisinesRaw
        .split(/[,]+/)
        .map((s) => s.trim())
        .filter(Boolean),
    [cuisinesRaw],
  );

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setClientError(null);
    setValidationMsg(null);
    setResponse(null);
    try {
      const cuisines = cuisineChips;
      if (cuisines.length === 0) {
        setValidationMsg("Enter at least one cuisine (comma-separated).");
        return;
      }
      const res = await postRecommendations({
        location: location.trim(),
        budget: budget.trim(),
        cuisines,
        min_rating: minRating,
        notes: notes.trim() || null,
        limit,
      });
      setResponse(res);
    } catch (err) {
      if (err instanceof ApiError) {
        const d = parseValidationDetail(err);
        if (d?.message) {
          setValidationMsg(d.message);
        } else {
          setClientError(`Request failed (HTTP ${err.status}).`);
        }
      } else {
        setClientError(err instanceof Error ? err.message : "Unknown error");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-surface">
      <header className="sticky top-0 z-10 border-b border-zinc-200/90 bg-surface-card/95 shadow-sm backdrop-blur-sm">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-4 py-3.5">
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-extrabold tracking-tight text-ink md:text-xl">
              Discover<span className="text-brand">.</span>
            </span>
            <span className="rounded-pill border border-brand/25 bg-brand-muted px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-brand">
              Demo
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 pb-16 pt-8 md:pt-10">
        <section className="mb-10 md:mb-12" aria-labelledby="hero-heading">
          <h1 id="hero-heading" className="text-3xl font-extrabold leading-tight tracking-tight text-ink md:text-4xl">
            Find food you&apos;ll love — <span className="text-brand">fast &amp; simple</span>
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-relaxed text-ink-secondary md:text-lg">
            Tell us your city, budget, and cuisines. We rank restaurants with clear explanations — same flow as
            discovery-first food apps, wired to your local API.
          </p>
        </section>

        <section className="mb-10 grid grid-cols-1 gap-3 sm:grid-cols-3" aria-label="Highlights">
          {[
            { k: "1-step", title: "Your tastes", sub: "Location, budget, cuisines" },
            { k: "2-step", title: "Smart match", sub: "Filters + ranking pipeline" },
            { k: "3-step", title: "Ranked picks", sub: "Ratings & short reasons" },
          ].map((s) => (
            <div
              key={s.k}
              className="rounded-card border border-zinc-100 bg-surface-card px-4 py-4 text-center shadow-card"
            >
              <p className="text-xs font-bold uppercase tracking-wide text-brand">{s.title}</p>
              <p className="mt-1 text-xs text-ink-secondary">{s.sub}</p>
            </div>
          ))}
        </section>

        <form
          onSubmit={onSubmit}
          aria-label="Recommendation preferences"
          aria-busy={loading}
          className="space-y-5 rounded-card border border-zinc-100 bg-surface-card p-6 shadow-card md:p-8"
        >
          <div className="border-b border-zinc-100 pb-1">
            <h2 className="text-lg font-bold text-ink">Preferences</h2>
            <p className="mt-1 text-sm text-ink-secondary">One primary action: get recommendations.</p>
          </div>

          <div className="grid gap-5 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label htmlFor="location" className={labelClass}>
                Location
              </label>
              <input
                id="location"
                name="location"
                required
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className={inputClass}
                autoComplete="address-level2"
              />
            </div>
            <div>
              <label htmlFor="budget" className={labelClass}>
                Budget
              </label>
              <input
                id="budget"
                name="budget"
                required
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                placeholder="medium, high, or e.g. 1500"
                className={inputClass}
              />
            </div>
            <div>
              <label htmlFor="min_rating" className={labelClass}>
                Minimum rating
              </label>
              <input
                id="min_rating"
                name="min_rating"
                type="number"
                step="0.1"
                min={0}
                max={5}
                required
                value={minRating}
                onChange={(e) => setMinRating(Number(e.target.value))}
                className={inputClass}
              />
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="cuisines" className={labelClass}>
                Cuisines <span className="font-normal text-ink-secondary">(comma-separated)</span>
              </label>
              <input
                id="cuisines"
                name="cuisines"
                required
                value={cuisinesRaw}
                onChange={(e) => setCuisinesRaw(e.target.value)}
                className={inputClass}
              />
              {cuisineChips.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2" aria-label="Cuisine chips">
                  {cuisineChips.map((c) => (
                    <span
                      key={c}
                      className="rounded-pill border border-zinc-200 bg-zinc-50 px-3 py-1 text-xs font-medium text-ink"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div>
              <label htmlFor="limit" className={labelClass}>
                Top N
              </label>
              <input
                id="limit"
                name="limit"
                type="number"
                min={1}
                max={50}
                required
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className={inputClass}
              />
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="notes" className={labelClass}>
                Notes <span className="font-normal text-ink-secondary">(optional)</span>
              </label>
              <textarea
                id="notes"
                name="notes"
                rows={2}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className={inputClass}
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-brand px-6 py-3.5 text-sm font-bold text-brand-foreground shadow-md transition hover:bg-brand-hover focus:outline-none focus:ring-2 focus:ring-brand/40 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto sm:min-w-[200px]"
          >
            {loading ? "Finding picks…" : "Get recommendations"}
          </button>
        </form>

        <div className="mt-10 space-y-4" aria-live="polite">
          {validationMsg && (
            <div
              role="alert"
              className="rounded-card border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900 shadow-sm"
            >
              <strong>Check input</strong> — {validationMsg}
            </div>
          )}
          {clientError && (
            <div
              role="alert"
              className="rounded-card border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900 shadow-sm"
            >
              {clientError}
            </div>
          )}
          {response && (
            <>
              <ExperienceBanner experience={response.experience} degraded={response.degraded} />
              {response.messages.length > 0 && (
                <details className="rounded-card border border-zinc-100 bg-surface-card p-4 text-sm text-ink-secondary shadow-card">
                  <summary className="cursor-pointer font-semibold text-ink">Diagnostics</summary>
                  <ul className="mt-2 list-disc space-y-1 pl-5">
                    {response.messages.map((m) => (
                      <li key={m}>{m}</li>
                    ))}
                  </ul>
                </details>
              )}
              <section aria-label="Recommendations results">
                <h2 className="mb-4 text-lg font-bold text-ink">Top picks</h2>
                {response.results.length === 0 ? null : (
                  <ol className="space-y-4">
                    {response.results.map((r) => (
                      <li key={`${r.id}-${r.rank}`}>
                        <article className="overflow-hidden rounded-card border border-zinc-100 bg-surface-card shadow-card transition hover:shadow-md">
                          <div className="border-l-4 border-brand pl-5 pr-5 pt-5">
                            <div className="flex flex-wrap items-start justify-between gap-2">
                              <h3 className="text-lg font-bold leading-snug text-ink md:text-xl">
                                <span className="mr-2 font-extrabold text-brand">#{r.rank}</span>
                                {r.name}
                              </h3>
                              <span className="inline-flex shrink-0 items-center gap-1 rounded-pill bg-amber-50 px-2.5 py-1 text-sm font-bold text-amber-950 ring-1 ring-amber-200/80">
                                <span aria-hidden>★</span>
                                {r.rating.toFixed(1)}
                              </span>
                            </div>
                            <p className="mt-2 flex flex-wrap gap-2 text-sm text-ink-secondary">
                              <span>{r.city}</span>
                              <span aria-hidden className="text-zinc-300">
                                ·
                              </span>
                              <span className="capitalize">{r.cost_band}</span>
                            </p>
                            <div className="mt-2 flex flex-wrap gap-2">
                              {r.cuisines.map((c) => (
                                <span
                                  key={c}
                                  className="rounded-pill bg-zinc-100 px-2.5 py-0.5 text-xs font-semibold text-ink"
                                >
                                  {c}
                                </span>
                              ))}
                            </div>
                          </div>
                          <p className="border-t border-zinc-50 px-5 py-4 text-sm leading-relaxed text-ink">
                            {r.explanation}
                          </p>
                        </article>
                      </li>
                    ))}
                  </ol>
                )}
              </section>
            </>
          )}
        </div>

        <footer className="mt-14 rounded-card border border-dashed border-zinc-200 bg-white/60 px-4 py-4 text-center text-xs text-ink-secondary">
          <code className="rounded-md bg-zinc-100 px-1.5 py-0.5 font-mono text-[11px]">POST /v1/recommendations</code>
          <span className="mx-1.5 text-zinc-300">·</span>
          <code className="rounded-md bg-zinc-100 px-1.5 py-0.5 font-mono text-[11px]">{apiBaseDisplay}</code>
          <br />
          <span className="mt-2 inline-block">
            Set <code className="font-mono text-ink">NEXT_PUBLIC_API_BASE_URL</code> and API{" "}
            <code className="font-mono text-ink">CORS_ORIGINS=http://localhost:3000</code> as needed.
          </span>
        </footer>
      </main>
    </div>
  );
}
