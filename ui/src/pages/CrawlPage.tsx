import React from "react";
import { useSearchParams } from "react-router-dom";
import { triggerCrawl } from "../services/api";
import CrawlEvents from "../components/CrawlEvents";

function CrawlPage() {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();

  const jobId = searchParams.get("jobId");

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    try {
      const job = await triggerCrawl();
      setSearchParams({ jobId: job.job_id });
    } catch {
      setError("Failed to trigger crawl. Make sure the server is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="w-full max-w-7xl mx-auto grow px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6 flex items-center justify-between gap-4">
        <h1 className="text-3xl font-bold text-gray-900">Crawler</h1>

        <button
          onClick={handleStart}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Starting..." : "Start Crawler"}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      <CrawlEvents jobId={jobId} />
    </main>
  );
}

export default CrawlPage;
