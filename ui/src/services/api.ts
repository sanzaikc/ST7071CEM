import type {
  SearchResponse,
  StatsResponse,
  CrawlJobCreate,
  CrawlJobResponse,
} from "../types/api";

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

export async function triggerCrawl(
  crawlData: CrawlJobCreate,
): Promise<CrawlJobResponse> {
  const response = await fetch(`${API_BASE_URL}/crawl/trigger`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(crawlData),
  });

  if (!response.ok) {
    throw new Error("Failed to trigger crawl");
  }

  return (await response.json()) as CrawlJobResponse;
}

export async function getCrawlStatus(jobId: string): Promise<CrawlJobResponse> {
  const response = await fetch(`${API_BASE_URL}/crawl/status/${jobId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch crawl status");
  }

  return (await response.json()) as CrawlJobResponse;
}

export async function getCrawlJobs(limit = 10): Promise<CrawlJobResponse[]> {
  const response = await fetch(`${API_BASE_URL}/crawl/jobs?limit=${limit}`);
  if (!response.ok) {
    throw new Error("Failed to fetch crawl jobs");
  }

  return (await response.json()) as CrawlJobResponse[];
}
