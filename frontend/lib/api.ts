import type { RecommendationRequest, RecommendationResponse, ValidationErrorDetail } from "./types";

export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(status: number, body: unknown) {
    super(`API error ${status}`);
    this.status = status;
    this.body = body;
  }
}

function apiBase(): string {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");
  if (!base) {
    return "http://127.0.0.1:8000";
  }
  return base;
}

export async function postRecommendations(
  body: RecommendationRequest,
): Promise<RecommendationResponse> {
  const res = await fetch(`${apiBase()}/v1/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new ApiError(res.status, data);
  }

  return data as RecommendationResponse;
}

export function parseValidationDetail(err: ApiError): ValidationErrorDetail | null {
  if (err.status !== 400 || !err.body || typeof err.body !== "object") {
    return null;
  }
  const d = (err.body as { detail?: ValidationErrorDetail }).detail;
  return d && typeof d === "object" ? d : null;
}
