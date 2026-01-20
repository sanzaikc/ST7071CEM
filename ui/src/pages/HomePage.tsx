import React from "react";
import SearchBox from "../components/SearchBox";
import PublicationCard from "../components/PublicationCard";
import { searchPublications } from "../services/api";
import type { PublicationResponse } from "../types/api";
import Placeholder from "../components/Placeholder";
import Loader from "../components/Loader";
import Error from "../components/Error";

function HomePage() {
  const [results, setResults] = React.useState<PublicationResponse[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [totalResults, setTotalResults] = React.useState(0);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    setSearchQuery(query);

    try {
      const data = await searchPublications(query, 50, 1);
      setResults(data.results);
      setTotalResults(data.total);
    } catch {
      setError(
        "Failed to search. Please make sure the backend server is running.",
      );
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-7xl mx-auto grow px-4 sm:px-6 lg:px-8 py-8">
      {/* Search Section */}
      <div className="mb-8">
        <SearchBox onSearch={handleSearch} loading={loading} />
      </div>

      <Error error={error} />

      {(() => {
        if (loading) return <Loader />;

        if (!searchQuery) return <Placeholder />;

        return (
          <>
            <div className="mb-6">
              <p className="text-gray-600">
                {totalResults > 0 ? (
                  <>
                    About{" "}
                    <span className="font-semibold">
                      {totalResults.toLocaleString()}
                    </span>{" "}
                    results for "
                    <span className="font-semibold">{searchQuery}</span>"
                  </>
                ) : (
                  <>
                    No results found for "
                    <span className="font-semibold">{searchQuery}</span>"
                  </>
                )}
              </p>
            </div>

            <div className="space-y-4">
              {results.map((publication, index) => (
                <PublicationCard
                  key={publication._id || index}
                  publication={publication}
                  rank={index + 1}
                  highlightQuery={searchQuery}
                />
              ))}
            </div>
          </>
        );
      })()}
    </main>
  );
}

export default HomePage;
