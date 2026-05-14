"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { ResearchHistoryItem, listReports } from "@/services/api";

const stopwords = new Set([
  "about",
  "ai",
  "and",
  "for",
  "from",
  "latest",
  "news",
  "recent",
  "the",
  "this",
  "week",
  "with",
]);

export function DashboardView() {
  const [reports, setReports] = useState<ResearchHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadReports() {
      try {
        setReports(await listReports(100));
      } finally {
        setIsLoading(false);
      }
    }

    loadReports();
  }, []);

  const stats = useMemo(() => {
    const totalSources = reports.reduce(
      (total, report) => total + report.source_count,
      0,
    );
    const extractedArticles = reports.reduce(
      (total, report) => total + report.article_count,
      0,
    );
    const topicCounts = reports
      .flatMap((report) => report.query.toLowerCase().match(/[a-z0-9]+/g) ?? [])
      .filter((term) => term.length > 2 && !stopwords.has(term))
      .reduce<Record<string, number>>((counts, term) => {
        counts[term] = (counts[term] ?? 0) + 1;
        return counts;
      }, {});
    const topics = Object.entries(topicCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    return {
      totalReports: reports.length,
      totalSources,
      extractedArticles,
      averageSources: reports.length
        ? Math.round((totalSources / reports.length) * 10) / 10
        : 0,
      topics,
    };
  }, [reports]);

  return (
    <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-950">Dashboard</h1>
          <p className="mt-2 text-sm leading-6 text-neutral-600">
            Activity overview for saved research reports.
          </p>
        </div>
        <Link
          className="rounded-md bg-teal-700 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-800"
          href="/"
        >
          New research
        </Link>
      </div>

      {isLoading ? (
        <p className="rounded-lg border border-neutral-200 bg-white p-5 text-sm text-neutral-600 shadow-sm">
          Loading dashboard...
        </p>
      ) : (
        <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
          <section className="grid gap-4 sm:grid-cols-2">
            <Metric label="Reports" value={stats.totalReports.toString()} />
            <Metric label="Sources" value={stats.totalSources.toString()} />
            <Metric
              label="Extracted"
              value={stats.extractedArticles.toString()}
            />
            <Metric label="Avg sources" value={stats.averageSources.toString()} />
          </section>

          <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
            <h2 className="text-base font-semibold text-neutral-950">
              Frequent Topics
            </h2>
            <div className="mt-4 grid gap-3">
              {stats.topics.length ? (
                stats.topics.map(([topic, count]) => (
                  <div className="grid gap-2" key={topic}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium capitalize text-neutral-800">
                        {topic}
                      </span>
                      <span className="text-neutral-500">{count}</span>
                    </div>
                    <div className="h-2 rounded-full bg-neutral-100">
                      <div
                        className="h-2 rounded-full bg-sky-500"
                        style={{
                          width: `${Math.min(100, Math.max(14, count * 22))}%`,
                        }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm leading-6 text-neutral-600">
                  No topic data yet.
                </p>
              )}
            </div>
          </section>

          <section className="rounded-lg border border-neutral-200 bg-white shadow-sm lg:col-span-2">
            <div className="border-b border-neutral-200 p-5">
              <h2 className="text-base font-semibold text-neutral-950">
                Recent Activity
              </h2>
            </div>
            <div className="divide-y divide-neutral-200">
              {reports.slice(0, 8).map((report) => (
                <Link
                  className="grid gap-2 p-5 hover:bg-amber-50 sm:grid-cols-[1fr_auto]"
                  href={`/reports/${report.id}`}
                  key={report.id}
                >
                  <span className="text-sm font-medium text-neutral-950">
                    {report.title}
                  </span>
                  <span className="text-sm text-neutral-500">
                    {formatDate(report.generated_at)}
                  </span>
                </Link>
              ))}
              {!reports.length ? (
                <p className="p-5 text-sm text-neutral-600">
                  No saved reports yet.
                </p>
              ) : null}
            </div>
          </section>
        </div>
      )}
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-neutral-500">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-neutral-950">{value}</p>
    </div>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
