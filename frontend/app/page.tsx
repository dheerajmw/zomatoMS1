"use client";

import { FormEvent, useMemo, useState } from "react";
import { ApiError, parseValidationDetail, postRecommendations } from "@/lib/api";
import type { RecommendationResponse } from "@/lib/types";

const inputClass =
  "mt-1.5 w-full rounded-xl border border-zinc-200/90 bg-white px-3.5 py-2.5 text-sm text-ink shadow-[0_1px_2px_rgba(0,0,0,0.04)] transition placeholder:text-ink-secondary/55 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/15";

const labelClass = "block text-sm font-semibold tracking-tight text-ink";

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
      <header className="sticky top-0 z-10 border-b border-zinc-200/80 bg-white shadow-[0_1px_0_rgba(0,0,0,0.03)]">
        <div className="mx-auto flex max-w-3xl items-center px-4 py-4 md:py-[1.125rem]">
          <div className="flex items-center gap-2.5">
            <span className="text-[1.125rem] font-extrabold tracking-tight text-ink md:text-xl">
              Discover<span className="text-brand">.</span>
            </span>
            <span className="rounded-pill border border-brand/20 bg-brand-muted px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-[0.14em] text-brand">
              Demo
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 pb-20 pt-9 md:pt-11">
        <section className="mb-11 md:mb-14" aria-labelledby="hero-heading">
          <h1
            id="hero-heading"
            className="text-[1.65rem] font-extrabold leading-[1.15] tracking-tight text-ink sm:text-3xl md:text-[2.125rem] md:leading-tight"
          >
            Find food you&apos;ll love — <span className="text-brand">fast &amp; simple</span>
          </h1>
          <p className="mt-4 max-w-2xl text-[0.9375rem] leading-relaxed text-ink-secondary md:text-lg md:leading-relaxed">
            Tell us your city, budget, and cuisines. We rank restaurants with clear explanations — same flow as
            discovery-first food apps, wired to your local API.
          </p>
        </section>

        <section className="mb-11 grid grid-cols-1 gap-3 sm:grid-cols-3 sm:gap-4" aria-label="Highlights">
          {[
            { k: "1", title: "Your tastes", sub: "Location, budget, cuisines" },
            { k: "2", title: "Smart match", sub: "Filters + ranking pipeline" },
            { k: "3", title: "Ranked picks", sub: "Ratings & short reasons" },
          ].map((s) => (
            <div
              key={s.k}
              className="rounded-card border border-zinc-100 bg-white px-5 py-5 text-center shadow-card"
            >
              <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-brand">{s.title}</p>
              <p className="mt-2 text-[13px] leading-snug text-ink-secondary">{s.sub}</p>
            </div>
          ))}
        </section>

        <form
          onSubmit={onSubmit}
          aria-label="Recommendation preferences"
          aria-busy={loading}
          className="space-y-6 rounded-card border border-zinc-100/90 bg-white p-6 shadow-preferences md:p-9"
        >
          <div className="border-b border-zinc-100 pb-4">
            <h2 className="text-lg font-bold tracking-tight text-ink">Preferences</h2>
            <p className="mt-1 text-sm text-ink-secondary">One primary action: get recommendations.</p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2">
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
                <div className="mt-2.5 flex flex-wrap gap-2" aria-label="Cuisine chips">
                  {cuisineChips.map((c) => (
                    <span
                      key={c}
                      className="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-800"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div className="sm:col-span-2 sm:max-w-[200px]">
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
            className="w-full rounded-xl bg-brand px-6 py-3.5 text-sm font-bold text-brand-foreground shadow-[0_4px_14px_rgba(226,55,68,0.35)] transition hover:bg-brand-hover hover:shadow-[0_6px_20px_rgba(226,55,68,0.4)] focus:outline-none focus:ring-2 focus:ring-brand/35 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto sm:min-w-[220px]"
          >
            {loading ? "Finding picks…" : "Get recommendations"}
          </button>
        </form>

        <div className="mt-11 space-y-4" aria-live="polite">
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
                <details className="rounded-card border border-zinc-100 bg-white p-4 text-sm text-ink-secondary shadow-card">
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
                        <article className="overflow-hidden rounded-card border border-zinc-100 bg-white shadow-card transition hover:shadow-md">
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

        <footer className="mt-16 rounded-card border border-dashed border-zinc-200/90 bg-white/70 px-4 py-4 text-center text-xs text-ink-secondary">
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
