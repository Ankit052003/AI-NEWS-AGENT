"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ResearchHistoryItem, listReports } from "@/services/api";

export function ReportList() {
  const [reports, setReports] = useState<ResearchHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadReports() {
      try {
        const response = await listReports(100);
        setReports(response);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Could not load reports.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    loadReports();
  }, []);

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-950">
            Saved Reports
          </h1>
          <p className="mt-2 text-sm leading-6 text-neutral-600">
            Reopen previous research runs and their source lists.
          </p>
        </div>
        <Link
          className="rounded-md bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800"
          href="/"
        >
          New research
        </Link>
      </div>

      <section className="rounded-lg border border-neutral-200 bg-white shadow-sm">
        {isLoading ? (
          <p className="p-5 text-sm text-neutral-600">Loading reports...</p>
        ) : null}

        {error ? (
          <p className="m-5 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
            {error}
          </p>
        ) : null}

        {!isLoading && !error && reports.length === 0 ? (
          <p className="p-5 text-sm text-neutral-600">No saved reports yet.</p>
        ) : null}

        {!isLoading && !error && reports.length > 0 ? (
          <div className="divide-y divide-neutral-200">
            {reports.map((report) => (
              <Link
                className="grid gap-3 p-5 hover:bg-sky-50 md:grid-cols-[minmax(0,1fr)_180px]"
                href={`/reports/${report.id}`}
                key={report.id}
              >
                <div>
                  <h2 className="text-base font-semibold text-neutral-950">
                    {report.title}
                  </h2>
                  <p className="mt-2 line-clamp-2 text-sm leading-6 text-neutral-600">
                    {report.summary}
                  </p>
                </div>
                <div className="text-sm text-neutral-600 md:text-right">
                  <p>{formatDate(report.generated_at)}</p>
                  <p className="mt-1">
                    {report.source_count} sources, {report.article_count} extracted
                  </p>
                </div>
              </Link>
            ))}
          </div>
        ) : null}
      </section>
    </main>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
