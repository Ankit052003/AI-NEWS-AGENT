const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type ResearchSource = {
  title: string;
  url: string;
  source: string;
  snippet: string;
  published_date: string | null;
};

export type ExtractedArticle = {
  title: string;
  url: string;
  source: string;
  extracted_text: string;
  word_count: number;
  author: string | null;
  published_date: string | null;
  extracted_at: string;
};

export type ArticleSummary = {
  citation_index: number;
  title: string;
  url: string;
  source: string;
  summary: string;
  key_points: string[];
  published_date: string | null;
};

export type ResearchResponse = {
  query_id: string | null;
  report_id: string | null;
  query: string;
  summary: string;
  report: string;
  sources: ResearchSource[];
  articles: ExtractedArticle[];
  article_summaries: ArticleSummary[];
  generated_at: string;
};

export type ResearchHistoryItem = {
  id: string;
  query_id: string;
  query: string;
  title: string;
  summary: string;
  status: string;
  source_count: number;
  article_count: number;
  generated_at: string;
};

export type SavedArticle = {
  id: string;
  title: string;
  url: string;
  source: string;
  snippet: string | null;
  published_date: string | null;
  extracted_text: string | null;
  summary: string | null;
  word_count: number | null;
  created_at: string;
};

export type SavedReport = {
  id: string;
  query_id: string;
  query: string;
  title: string;
  summary: string;
  report: string;
  status: string;
  sources: ResearchSource[];
  articles: SavedArticle[];
  generated_at: string;
};

type ResearchPayload = {
  query: string;
  max_sources: number;
};

type ApiErrorPayload = {
  detail?: string;
};

export async function createResearch(
  payload: ResearchPayload,
): Promise<ResearchResponse> {
  return apiFetch<ResearchResponse>("/research", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listReports(limit = 20): Promise<ResearchHistoryItem[]> {
  return apiFetch<ResearchHistoryItem[]>(`/research/history?limit=${limit}`);
}

export async function getReport(reportId: string): Promise<SavedReport> {
  return apiFetch<SavedReport>(
    `/research/reports/${encodeURIComponent(reportId)}`,
  );
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!headers.has("Content-Type") && init?.body) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    let message = "Request failed";
    try {
      const payload = (await response.json()) as ApiErrorPayload;
      message = payload.detail ?? message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}
