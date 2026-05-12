# Problem Statement: AI-Powered Restaurant Recommendation System (Zomato-Inspired)

## Context

You are building a **restaurant recommendation service** inspired by Zomato. The system should suggest restaurants by combining **structured restaurant data** with a **large language model (LLM)** so that recommendations feel personalized and easy to understand—not only a sorted list of rows from a database.

## Problem

Users often have several constraints at once (location, budget, cuisine, minimum quality) and want **short, trustworthy explanations** for why a place fits them. A pure filter-and-sort UI answers “what matches” but not “why these picks.” The product goal is to **filter real data first**, then **use an LLM to rank, compare, and explain** a small shortlist in natural language.

## Objectives

Design and implement an application that:

1. **Accepts user preferences**—for example: area or city, budget band, cuisine, minimum rating, and optional notes (family-friendly, quick service, outdoor seating, etc.).
2. **Uses a real-world restaurant dataset** as the source of truth for names, locations, cuisines, cost, ratings, and related fields.
3. **Integrates an LLM** so recommendations are ranked and summarized in a human-readable way on top of the structured matches.
4. **Presents results clearly**—top picks with key facts plus short AI-generated rationale.

## Dataset

- **Source:** [Zomato restaurant recommendation dataset on Hugging Face](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) (`ManikaSaini/zomato-restaurant-recommendation`).
- **Ingestion:** Load the dataset, clean or normalize fields as needed, and retain attributes required for filtering and display (e.g., restaurant name, location, cuisines, approximate cost, rating, and any other columns useful for matching and explanation).

## System Workflow

### 1. Data ingestion

- Load and preprocess the dataset.
- Map columns to a consistent internal schema (names, types, missing-value handling).
- Keep enough context in each record for both **rule-based filtering** and **LLM prompts** (without sending unnecessary sensitive or huge blobs if not needed).

### 2. User input

Collect preferences, for example:

- **Location** (e.g., city or area: Delhi, Bangalore, etc.).
- **Budget** (e.g., low / medium / high, or numeric bands aligned to the dataset’s cost field).
- **Cuisine** (e.g., Italian, Chinese, North Indian).
- **Minimum rating** (threshold on the dataset’s rating scale).
- **Optional constraints** (e.g., family-friendly, fast service, suitable for groups).

Validate inputs and map them to the dataset’s vocabulary where labels differ (e.g., cost categories).

### 3. Integration layer

- **Filter** restaurants to a candidate set that satisfies hard constraints (location, budget, cuisine, minimum rating, etc.).
- **Prepare a compact structured payload** for the LLM (e.g., JSON or bullet list of top *N* candidates with the fields needed to compare and rank).
- **Design prompts** that instruct the LLM to: only recommend from the provided candidates, respect user constraints, rank or re-order with justification, and avoid inventing venues or facts not present in the payload.

### 4. Recommendation engine

Use the LLM to:

- **Rank** (or re-rank) candidates from the filtered set.
- **Summarize** trade-offs when useful (e.g., “slightly farther but better rated and within budget”).
- **Stay grounded** in the supplied data; hallucinated restaurants or ratings are unacceptable for this use case.

### 5. Output display

Present the **top recommendations** in a clear UI or API response, typically including:

| Element | Purpose |
|--------|---------|
| Restaurant name | Identity |
| Location / area | Fit to place |
| Cuisine(s) | Fit to taste |
| Rating | Quality signal |
| Estimated cost / budget band | Fit to wallet |
| Short LLM explanation | Why this pick for *this* user |

Exact layout is flexible; the requirement is **scannable facts + a brief, personalized rationale**.

## Success Criteria (Suggested)

- End-to-end path works: **dataset → filters → LLM → rendered results**.
- Recommendations are **traceable** to rows that passed the filters.
- Prompting strategy is documented enough to reproduce behavior (temperature, model choice, and guardrails).
- Basic robustness: sensible behavior for **no matches**, **too many matches**, or **missing fields** in the dataset.

## Out of Scope (Unless You Extend the Project)

- Live Zomato API integration, payments, or real orders.
- User accounts and long-term preference learning (unless explicitly added later).
