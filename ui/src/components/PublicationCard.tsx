import type { PublicationAuthor, PublicationResponse } from "../types/api";

function formatAuthors(authors: PublicationAuthor[] | undefined): string {
  if (!authors || authors.length === 0) return "Unknown";

  const authorNames = authors.map((a) => a.name);
  if (authorNames.length === 1) return authorNames[0]!;
  if (authorNames.length === 2) return authorNames.join(" and ");
  return `${authorNames[0]} et al.`;
}

function getTypeColor(type: PublicationResponse["publication_type"]) {
  const colors: Record<string, string> = {
    journal_article: "bg-blue-100 text-blue-800",
    conference_paper: "bg-green-100 text-green-800",
    book: "bg-purple-100 text-purple-800",
    other: "bg-gray-100 text-gray-800",
  };
  return colors[type] || colors.other;
}

export default function PublicationCard({
  publication,
  rank,
}: {
  publication: PublicationResponse;
  rank: number;
}) {
  const {
    title,
    authors,
    year,
    abstract,
    publication_type,
    publication_url,
    cosine_similarity,
  } = publication;

  return (
    <div className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow border border-gray-200">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-semibold text-sm">
            {rank}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="text-xl font-semibold text-primary-900 mb-2 hover:text-primary-600 cursor-pointer line-clamp-2">
            {title || "Untitled"}
          </h3>

          <p className="text-sm text-gray-600 mb-2">
            {formatAuthors(authors)} - {year || "N/A"}
          </p>

          {publication_type && (
            <span
              className={`inline-block px-2 py-1 text-xs font-medium rounded ${getTypeColor(publication_type)} mb-3`}
            >
              {publication_type.replace("_", " ")}
            </span>
          )}

          {abstract && (
            <p className="text-gray-700 text-sm line-clamp-3 mb-3">{abstract}</p>
          )}

          <div className="flex items-center justify-between">
            <div className="flex gap-3 text-sm">
              {publication_url && (
                <a
                  href={publication_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-800 hover:underline"
                >
                  View Publication
                </a>
              )}
            </div>

            {cosine_similarity !== undefined && cosine_similarity !== null && (
              <span className="text-xs text-gray-500">
                Relevance: {(cosine_similarity * 100).toFixed(1)}%
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

