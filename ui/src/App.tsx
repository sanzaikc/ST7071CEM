import { useState, useEffect } from "react";
import SearchBox from "./components/SearchBox";
import PublicationCard from "./components/PublicationCard";
import { searchPublications, getStatistics } from "./services/api";
import type { PublicationResponse, StatsResponse } from "./types/api";

function App() {
  const [results, setResults] = useState<PublicationResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [totalResults, setTotalResults] = useState(0);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const data = await getStatistics();
      setStats(data);
    } catch (err: unknown) {
      console.error("Failed to load statistics:", err);
    }
  };

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
        "Failed to search. Please make sure the backend server is running."
      );
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Coventry Research
                </h1>
                <p className="text-sm text-gray-600">
                  Publications Search Engine
                </p>
              </div>
            </div>

            {stats && (
              <div className="hidden md:flex items-center gap-6 text-sm">
                <div className="text-center">
                  <div className="font-semibold text-gray-900">
                    {stats.total_publications?.toLocaleString() || 0}
                  </div>
                  <div className="text-gray-600">Publications</div>
                </div>
                <div className="text-center">
                  <div className="font-semibold text-gray-900">
                    {stats.total_authors?.toLocaleString() || 0}
                  </div>
                  <div className="text-gray-600">Authors</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <SearchBox onSearch={handleSearch} loading={loading} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {searchQuery && !loading && (
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
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="text-center">
              <svg
                className="animate-spin h-12 w-12 text-primary-600 mx-auto mb-4"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <p className="text-gray-600">Searching...</p>
            </div>
          </div>
        )}

        {/* Results List */}
        {!loading && results.length > 0 && (
          <div className="space-y-4">
            {results.map((publication, index) => (
              <PublicationCard
                key={publication._id || index}
                publication={publication}
                rank={index + 1}
              />
            ))}
          </div>
        )}

        {/* Welcome State */}
        {!loading && !searchQuery && (
          <div className="text-center py-16">
            <svg
              className="w-24 h-24 text-gray-300 mx-auto mb-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Search Coventry Research Publications
            </h2>
            <p className="text-gray-600 mb-6">
              Find publications, authors, and research topics from Coventry.
            </p>
            <div className="max-w-md mx-auto text-left bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-3">Search Tips:</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 mt-0.5">•</span>
                  <span>
                    Use specific keywords related to your research interest
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 mt-0.5">•</span>
                  <span>
                    Search by author name, publication title, or topic
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-600 mt-0.5">•</span>
                  <span>
                    Results are ranked by relevance using TF-IDF scoring
                  </span>
                </li>
              </ul>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-600 text-sm">
            © 2026 Coventry University Research Search Engine
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
