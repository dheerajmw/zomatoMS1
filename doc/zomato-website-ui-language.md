# Zomato.com — design & UI language reference

**Purpose:** Capture the **observable** marketing-site structure, **copy tone**, and **visual language** associated with [zomato.com](https://www.zomato.com) so this repo can align UI decisions without embedding Zomato assets or proprietary code.

**Scope:** Descriptive notes for designers/developers. Not an official Zomato document. For **exact** colours and type on the live site, use browser DevTools on the current production build.

**Official public design context:** Zomato documents its product design system as **Sushi** (components, foundations, principles). See [sushi.design](https://sushi.design/) and the announcement on [Zomato Technology (Medium)](https://medium.com/zomato-technology/zomatos-new-sushi-design-system-d7f4f98664c5). Typography direction (custom **Okra** face, related to geometric sans influences) is discussed on [Zomato’s blog — typography](https://blog.zomato.com/defining-our-typography-system).

---

## 1. Brand & product framing (from homepage messaging)

| Theme | How it shows up |
|--------|------------------|
| **Category leadership** | “India’s #1 food delivery app” — number-one positioning, national scale. |
| **Speed & ease** | “fast & easy online ordering”, “seamless” — low-friction promise. |
| **Discovery + delivery** | “discover new tastes, delivered right to your doorstep” — catalogue + logistics. |
| **Scale proof** | Large rounded stats (e.g. restaurants, cities, orders delivered) as trust anchors. |
| **Ecosystem** | Cross-links to Blinkit, District, Hyperpure — family of brands, horizontal scroll / card grid pattern on marketing pages. |
| **Monetisation / loyalty** | “GOLD”, “Free Delivery”, “extra off” — tiered benefits, savings-led language. |
| **App-first** | Repeated “Download the app”, QR codes, feature tiles (Veg Mode, Collections, Gourmet, etc.). |

**Tone keywords:** confident, metric-heavy, benefit-led, friendly mass-market (not luxury-minimal).

---

## 2. Information architecture (marketing homepage)

Typical vertical rhythm on the public homepage (content order may vary by region/A-B):

1. **Hero** — headline + subcopy + primary CTA toward app / ordering.
2. **Trust band** — 2–4 stat blocks (restaurants, cities, orders).
3. **Value proposition** — “Better food for more people” narrative block.
4. **Feature grid** — icon + label tiles (Veg Mode, Healthy, Offers, Gift Cards, …).
5. **Program promo** — Gold / savings program with bullet benefits.
6. **B2B / supply** — Hyperpure-style partner story.
7. **Sister brands** — Blinkit, District, etc. as cards with short pitch + “Check it out”.
8. **Footer CTA** — download app again, QR, store badges.

For a **restaurant discovery** experience (closer to this repo), product UI often shifts toward: **location → search → list/grid → detail → reviews/ratings**; marketing site is lighter on that IA but the **same vocabulary** (cities, offers, veg-forward filters) appears in product.

---

## 3. Visual language (patterns to mirror, not to copy pixel-perfect)

### Colour

- **Primary accent:** Strong **warm red** on white/light backgrounds for CTAs, key highlights, and brand marks. (Historic and commonly referenced brand reds include approximations such as `#E23744` / `#CB202D` — **verify live** in DevTools.)
- **Neutrals:** Off-white page background, **deep charcoal or near-black** for primary text, **mid grey** for secondary (meta, hints, disabled).
- **Semantic:** Green accents for veg / positive states where applicable; amber/orange for offers and attention (common in food-commerce).

### Typography

- **Headings:** Bold, tight tracking, large hierarchy jumps (hero H1 vs section H2).
- **Body:** High legibility sans-serif at comfortable line height; numeric stats often **extra-bold** and oversized.
- **Product note:** Internal apps use the **Okra** system; on the web, fallbacks are typically system or webfont stacks — match **weight and scale**, not necessarily the proprietary font file.

### Layout & density

- **Generous vertical spacing** between hero sections; **card-based** clusters for features and partner brands.
- **Rounded corners** on cards, buttons, and inputs (soft, consumer-friendly, not sharp-edged corporate).
- **Mobile-first** implied by app CTAs and narrow column reading width on small screens.

### Components & motifs

- **Pills / chips** for cuisines, offers, veg/non-veg, filters.
- **Star ratings** (often half-star affordances) next to restaurant names.
- **Imagery-forward** list cards: food photo, name, cuisine tags, price band, distance/time.
- **Primary button:** Solid fill, white label text, full-width on mobile where appropriate.
- **Secondary:** Outline or ghost on white; red text links for tertiary actions.

### Motion (inferred)

- Subtle scroll reveals on marketing; product lists often use **skeleton loaders** and short transitions on hover/tap — keep motion **functional**, not decorative.

---

## 4. Sushi design principles (from public write-ups)

Use as **UX guardrails** when extending this project’s UI:

1. **User centricity** — reduce steps to “find food → decide → order”.
2. **Inclusivity** — readable contrast, veg mode, regional language support where relevant.
3. **Simplicity** — one primary action per view when possible.
4. **Consistency** — repeat patterns for filters, cards, and errors across screens.

---

## 5. Suggested design tokens (for `frontend/` — approximate)

Use only as a **starting point**; tune against live zomato.com or brand guidelines.

| Token | Suggested role | Example (verify) |
|--------|------------------|------------------|
| `--color-brand-primary` | Buttons, links, focus ring | Sample red from site |
| `--color-brand-primary-hover` | Hover state | Darken ~6–8% |
| `--color-surface` | Page background | `#FAFAFA` or white |
| `--color-text-primary` | Headings, body | `#1C1C1C` range |
| `--color-text-secondary` | Meta, captions | `#696969` range |
| `--radius-card` | Cards, modals | `12px`–`16px` |
| `--radius-pill` | Chips, tabs | `9999px` or large px |
| `--shadow-card` | Resting card | Soft, low blur |
| `--font-heading-weight` | H1–H3 | `700` |
| `--font-body-weight` | Paragraph | `400`–`500` |

---

## 6. Sources & maintenance

| Source | URL |
|--------|-----|
| Live marketing / product shell | https://www.zomato.com |
| Design system hub | https://sushi.design/ |
| Sushi announcement | https://medium.com/zomato-technology/zomatos-new-sushi-design-system-d7f4f98664c5 |
| Typography blog | https://blog.zomato.com/defining-our-typography-system |

**Maintenance:** Revisit this file when Zomato ships major rebrands; re-sample colours in DevTools and update §5 tokens if the product diverges.

---

## 7. Legal / ethical note

Do not ship Zomato **logos**, **screenshots**, or **proprietary assets** as if they were this project’s brand. This document is **reference and inspiration** for a Zomato-**inspired** recommender UI only.
