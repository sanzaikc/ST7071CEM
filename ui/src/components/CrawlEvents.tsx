import React from "react";
import type { CrawlEvent } from "../types/api";

const WS_BASE_URL = "ws://localhost:8000";

export default function CrawlEvents({ jobId }: { jobId: string | null }) {
  const [events, setEvents] = React.useState<CrawlEvent[]>([]);
  const [error, setError] = React.useState<string | null>(null);

  const wsRef = React.useRef<WebSocket | null>(null);
  const pingRef = React.useRef<number | null>(null);

  const closeWs = React.useCallback(() => {
    if (pingRef.current != null) {
      window.clearInterval(pingRef.current);
      pingRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  React.useEffect(() => {
    setEvents([]);
    setError(null);

    if (!jobId) {
      closeWs();
      return;
    }

    closeWs();
    const ws = new WebSocket(`${WS_BASE_URL}/ws/crawl/${jobId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      pingRef.current = window.setInterval(() => {
        try {
          ws.send("ping");
        } catch {
          closeWs();
        }
      }, 15000);
    };

    ws.onmessage = (evt) => {
      try {
        const parsed = JSON.parse(evt.data) as CrawlEvent;
        setEvents((prev) => {
          const next = prev.length > 500 ? prev.slice(-400) : prev;
          return [...next, parsed];
        });
      } catch {
        return;
      }
    };

    ws.onerror = () => {
      setError("Live connection lost.");
      closeWs();
    };

    ws.onclose = () => {
      closeWs();
    };

    return () => {
      closeWs();
    };
  }, [jobId, closeWs]);

  const levelStyle = (level: CrawlEvent["level"]) => {
    switch (level) {
      case "error":
        return "text-red-900 bg-red-50 border-red-200";
      case "warn":
        return "text-amber-900 bg-amber-50 border-amber-200";
      case "success":
        return "text-emerald-900 bg-emerald-50 border-emerald-200";
      default:
        return "text-slate-700 bg-slate-50 border-slate-200";
    }
  };

  return (
    <div className="space-y-3">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
        <div className="overflow-auto p-3 space-y-2">
          {events.length ? (
            events
              .slice()
              .reverse()
              .map((e, idx) => (
                <div
                  key={`${e.ts}-${idx}`}
                  className={`text-xs border rounded p-2 ${levelStyle(e.level)}`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="font-semibold">
                      {e.stage}{" "}
                      <span className="font-normal text-gray-600">
                        {new Date(e.ts).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="uppercase tracking-wide">{e.level}</div>
                  </div>
                  <div className="mt-1">{e.message}</div>
                  {e.url ? (
                    <div className="mt-1 break-all">
                      <a
                        className="underline"
                        href={e.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {e.url}
                      </a>
                    </div>
                  ) : null}
                </div>
              ))
          ) : (
            <div className="text-sm text-gray-600 py-10 text-center">
              {jobId
                ? "Connected. Waiting for events..."
                : "Start the crawler to stream events."}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
