import type { SearchResponse, StatsResponse } from "../types/api";

const API_BASE_URL = "http://localhost:8000/api";

export async function searchPublications(
  query: string,
  limit = 20,
  page = 1,
): Promise<SearchResponse> {
  const url = new URL(`${API_BASE_URL}/search`);
  url.searchParams.set("q", query);
  url.searchParams.set("limit", String(limit));
  url.searchParams.set("page", String(page));

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error("Search failed");
  }

  return (await response.json()) as SearchResponse;
}

export async function getStatistics(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/stats`);
  if (!response.ok) {
    throw new Error("Failed to fetch statistics");
  }

  return (await response.json()) as StatsResponse;
}

