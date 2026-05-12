/** Types aligned with `src/recommender/domain/models.py` and `zomato_prefs` request wire model. */

export type BudgetBand = "low" | "medium" | "high";

export type RecommendationRequest = {
  location: string;
  budget: string;
  cuisines: string[];
  min_rating: number;
  notes?: string | null;
  limit: number;
};

export type RecommendationItem = {
  id: string;
  rank: number;
  name: string;
  city: string;
  cuisines: string[];
  rating: number;
  cost_band: BudgetBand;
  explanation: string;
};

export type ExperienceState = "ok" | "empty" | "degraded" | null;

export type RecommendationResponse = {
  request_id: string;
  match_count: number;
  capped_to: number | null;
  sent_to_llm: number | null;
  results: RecommendationItem[];
  degraded: boolean;
  experience: ExperienceState;
  messages: string[];
};

export type ValidationErrorDetail = {
  code?: string;
  message?: string;
  allowed?: unknown;
};
