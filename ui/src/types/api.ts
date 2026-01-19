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

