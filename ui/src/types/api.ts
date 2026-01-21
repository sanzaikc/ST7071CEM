export type IsoDateTimeString = string;

export type PublicationType =
  | "journal_article"
  | "conference_paper"
  | "book"
  | "book_chapter"
  | "thesis"
  | "report"
  | "other";

export interface PublicationAuthor {
  name: string;
  profile_url: string;
  pure_id: string;
}

export interface PublicationResponse {
  _id: string;
  pure_id: string;
  title: string;
  authors: PublicationAuthor[];
  year: number;
  publication_type: PublicationType;
  abstract?: string | null;
  keywords: string[];
  publication_url: string;
  doi?: string | null;
  external_url?: string | null;
  score?: number | null;
  cosine_similarity?: number | null;
  crawled_at: IsoDateTimeString;
  updated_at: IsoDateTimeString;
}

export interface SearchResponse {
  total: number;
  page: number;
  limit: number;
  results: PublicationResponse[];
}

export interface StatsResponse {
  total_publications: number;
  total_authors: number;
  publications_by_year: Record<string, number>;
  publications_by_type: Record<string, number>;
  last_crawl?: IsoDateTimeString | null;
}

export type CrawlType = "full" | "incremental" | "on_demand";
export type CrawlStatus = "pending" | "running" | "completed" | "failed";

export interface CrawlJobStats {
  authors_crawled: number;
  publications_found: number;
  new_publications: number;
  updated_publications: number;
  errors: number;
}

export interface CrawlJobCreate {
  crawl_type: CrawlType;
}

export interface CrawlJobResponse {
  _id: string;
  job_id: string;
  status: CrawlStatus;
  crawl_type: CrawlType;
  started_at: IsoDateTimeString;
  completed_at?: IsoDateTimeString | null;
  stats: CrawlJobStats;
  error_log: string[];
}

export type CrawlEventLevel = "info" | "success" | "warn" | "error";

export interface CrawlEvent {
  job_id: string;
  ts: IsoDateTimeString;
  level: CrawlEventLevel;
  stage: string;
  message: string;
  url?: string;
  counters?: Record<string, number>;
  data?: Record<string, unknown>;
}

export interface ClusterRequest {
  text: string;
}

export interface ClusterResponse {
  category: string;
  cluster_id?: number | null;
}
