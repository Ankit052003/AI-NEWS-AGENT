"use client";

import Link from "next/link";
import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";

import { ReportMarkdown } from "@/components/ReportMarkdown";
import {
  ResearchHistoryItem,
  ResearchResponse,
  createResearch,
  listReports,
} from "@/services/api";

const exampleQueries = [
  "Latest AI startup funding news this week",
  "Recent acquisitions in the AI industry",
  "Funding trends in AI healthcare startups",
];

const progressSteps = ["Search", "Extract", "Summarize", "Save"];

export function ResearchWorkspace() {
  const [query, setQuery] = useState(exampleQueries[0]);
  const [maxSources, setMaxSources] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [history, setHistory] = useState<ResearchHistoryItem[]>([]);

  const sourceCountLabel = useMemo(
    () => `${maxSources} source${maxSources === 1 ? "" : "s"}`,
    [maxSources],
  );

  useEffect(() => {
    let isActive = true;

    async function loadHistory() {
      try {
        const reports = await listReports(5);
        if (isActive) {
          setHistory(reports);
        }
      } catch {
        if (isActive) {
          setHistory([]);
        }
      }
    }

    loadHistory();

    return () => {
      isActive = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuery = query.trim();
    if (trimmedQuery.length < 3) {
      setError("Enter a longer research query.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await createResearch({
        query: trimmedQuery,
        max_sources: maxSources,
      });
      setResult(response);
      setHistory(await listReports(5));
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Research request failed.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="mx-auto grid w-full max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.35fr)]">
      <section className="space-y-5">
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold text-neutral-950">
                Research Workspace
              </h1>
              <p className="mt-2 text-sm leading-6 text-neutral-600">
                Run a source-backed news report and save it to history.
              </p>
            </div>
            <Link
              className="rounded-md border border-neutral-300 px-3 py-2 text-sm font-medium text-neutral-700 hover:border-teal-500 hover:text-teal-700"
              href="/dashboard"
            >
              Dashboard
            </Link>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <label className="block text-sm font-medium text-neutral-800" htmlFor="query">
              Research query
            </label>
            <textarea
              className="min-h-36 w-full resize-none rounded-md border border-neutral-300 px-4 py-3 text-base text-neutral-950 outline-none transition focus:border-teal-600 focus:ring-4 focus:ring-teal-100"
              id="query"
              name="query"
              onChange={(event) => setQuery(event.target.value)}
              value={query}
            />

            <div className="grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end">
              <div>
                <label
                  className="block text-sm font-medium text-neutral-800"
                  htmlFor="maxSources"
                >
                  Max sources
                </label>
                <div className="mt-2 flex items-center gap-3">
                  <input
                    className="w-full accent-teal-700"
                    id="maxSources"
                    max={10}
                    min={1}
                    onChange={(event) => setMaxSources(Number(event.target.value))}
                    type="range"
                    value={maxSources}
                  />
                  <span className="w-20 text-right text-sm font-medium text-neutral-700">
                    {sourceCountLabel}
                  </span>
                </div>
              </div>
              <button
                className="rounded-md bg-teal-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-neutral-400"
                disabled={isLoading}
                type="submit"
              >
                {isLoading ? "Running" : "Run research"}
              </button>
            </div>
          </form>

          {error ? (
            <p className="mt-4 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
              {error}
            </p>
          ) : null}
        </div>

        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold text-neutral-950">
            Example Queries
          </h2>
          <div className="mt-3 grid gap-2">
            {exampleQueries.map((example) => (
              <button
                className="rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2 text-left text-sm leading-6 text-neutral-700 hover:border-sky-300 hover:bg-sky-50 hover:text-sky-800"
                key={example}
                onClick={() => setQuery(example)}
                type="button"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        <RecentReports reports={history} />
      </section>

      <section className="min-h-[680px] rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        {isLoading ? <ProgressState /> : null}
        {!isLoading && result ? <ResearchResult result={result} /> : null}
        {!isLoading && !result ? <EmptyReportState /> : null}
      </section>
    </main>
  );
}

function ProgressState() {
  return (
    <div className="flex min-h-[620px] flex-col justify-center">
      <div className="mx-auto w-full max-w-md">
        <p className="text-sm font-medium text-teal-700">Research in progress</p>
        <h2 className="mt-2 text-2xl font-semibold text-neutral-950">
          Building the report
        </h2>
        <div className="mt-6 grid gap-3">
          {progressSteps.map((step) => (
            <div
              className="flex items-center justify-between rounded-md border border-neutral-200 px-4 py-3"
              key={step}
            >
              <span className="text-sm font-medium text-neutral-800">{step}</span>
              <span className="h-2.5 w-2.5 rounded-full bg-teal-600" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function EmptyReportState() {
  return (
    <div className="flex min-h-[620px] flex-col justify-center">
      <div className="mx-auto max-w-md text-center">
        <h2 className="text-2xl font-semibold text-neutral-950">
          Ready for a report
        </h2>
        <p className="mt-3 text-sm leading-6 text-neutral-600">
          The next completed research run will appear here with citations and
          saved source links.
        </p>
      </div>
    </div>
  );
}

function ResearchResult({ result }: { result: ResearchResponse }) {
  return (
    <div className="space-y-6">
      <div className="border-b border-neutral-200 pb-4">
        <div className="flex flex-wrap items-center gap-2 text-xs font-medium">
          <span className="rounded-md bg-teal-50 px-2.5 py-1 text-teal-800">
            {result.sources.length} sources
          </span>
          <span className="rounded-md bg-sky-50 px-2.5 py-1 text-sky-800">
            {result.articles.length} extracted
          </span>
          {result.report_id ? (
            <Link
              className="rounded-md bg-amber-50 px-2.5 py-1 text-amber-800 hover:text-amber-950"
              href={`/reports/${result.report_id}`}
            >
              Saved report
            </Link>
          ) : null}
        </div>
        <h2 className="mt-3 text-xl font-semibold text-neutral-950">
          {result.query}
        </h2>
        <p className="mt-2 text-sm leading-6 text-neutral-600">{result.summary}</p>
      </div>

      <ReportMarkdown content={result.report} />

      <div className="border-t border-neutral-200 pt-5">
        <h3 className="text-base font-semibold text-neutral-950">Sources</h3>
        <div className="mt-3 grid gap-3">
          {result.sources.map((source, index) => (
            <a
              className="rounded-md border border-neutral-200 p-3 text-sm hover:border-teal-300 hover:bg-teal-50"
              href={source.url}
              key={source.url}
              rel="noreferrer"
              target="_blank"
            >
              <span className="font-semibold text-neutral-950">
                [{index + 1}] {source.title}
              </span>
              <span className="mt-1 block text-neutral-600">{source.source}</span>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}

function RecentReports({ reports }: { reports: ResearchHistoryItem[] }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-neutral-950">Recent Reports</h2>
        <Link
          className="text-sm font-medium text-teal-700 hover:text-teal-900"
          href="/reports"
        >
          View all
        </Link>
      </div>
      <div className="mt-3 grid gap-3">
        {reports.length ? (
          reports.map((report) => (
            <Link
              className="rounded-md border border-neutral-200 p-3 hover:border-sky-300 hover:bg-sky-50"
              href={`/reports/${report.id}`}
              key={report.id}
            >
              <span className="block text-sm font-medium text-neutral-950">
                {report.title}
              </span>
              <span className="mt-1 block text-xs text-neutral-500">
                {formatDate(report.generated_at)} - {report.source_count} sources
              </span>
            </Link>
          ))
        ) : (
          <p className="text-sm leading-6 text-neutral-600">No saved reports yet.</p>
        )}
      </div>
    </div>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
