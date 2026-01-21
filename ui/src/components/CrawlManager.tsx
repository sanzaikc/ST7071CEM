import React from "react";
import { triggerCrawl } from "../services/api";
import type { CrawlType } from "../types/api";

function CrawlManager() {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState<string | null>(null);
  const [selectedCrawlType, setSelectedCrawlType] =
    React.useState<CrawlType>("full");

  const handleTriggerCrawl = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await triggerCrawl({ crawl_type: selectedCrawlType });
      setSuccess("Crawl triggered successfully!");
    } catch (err) {
      setError(
        err
          ? "Failed to trigger crawl. Make sure the server is running."
          : "An unknown error occurred.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Trigger Crawler
      </h2>

      <div className="flex flex-col sm:flex-row gap-4">
        <select
          value={selectedCrawlType}
          onChange={(e) => setSelectedCrawlType(e.target.value as CrawlType)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        >
          <option value="full">Full Crawl</option>
          <option value="incremental">Incremental Crawl</option>
          <option value="on_demand">On-Demand Crawl</option>
        </select>

        <button
          onClick={handleTriggerCrawl}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Triggering..." : "Start Crawl"}
        </button>
      </div>

      {success && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 text-sm">{success}</p>
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
}

export default CrawlManager;
