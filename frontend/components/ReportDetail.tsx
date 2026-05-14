"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ReportMarkdown } from "@/components/ReportMarkdown";
import { SavedReport, getReport } from "@/services/api";

type ReportDetailProps = {
  reportId: string;
};

export function ReportDetail({ reportId }: ReportDetailProps) {
  const [report, setReport] = useState<SavedReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadReport() {
      try {
        const response = await getReport(reportId);
        setReport(response);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Could not load report.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    loadReport();
  }, [reportId]);

  return (
    <main className="mx-auto grid w-full max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_340px]">
      <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
        <Link
          className="text-sm font-medium text-teal-700 hover:text-teal-900"
          href="/reports"
        >
          Back to reports
        </Link>

        {isLoading ? (
          <p className="mt-5 text-sm text-neutral-600">Loading report...</p>
        ) : null}

        {error ? (
          <p className="mt-5 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
            {error}
          </p>
        ) : null}

        {report ? (
          <div className="mt-5">
            <div className="border-b border-neutral-200 pb-4">
              <h1 className="text-2xl font-semibold text-neutral-950">
                {report.title}
              </h1>
              <p className="mt-2 text-sm text-neutral-500">
                {formatDate(report.generated_at)} - {report.status}
              </p>
              <p className="mt-3 text-sm leading-6 text-neutral-600">
                {report.summary}
              </p>
            </div>
            <ReportMarkdown content={report.report} />
          </div>
        ) : null}
      </section>

      <aside className="space-y-5">
        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold text-neutral-950">Sources</h2>
          <div className="mt-3 grid gap-3">
            {report?.sources.map((source, index) => (
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

        <div className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold text-neutral-950">
            Extracted Articles
          </h2>
          <div className="mt-3 grid gap-3">
            {report?.articles.map((article) => (
              <div className="rounded-md border border-neutral-200 p-3" key={article.id}>
                <p className="text-sm font-medium text-neutral-950">{article.title}</p>
                <p className="mt-1 text-xs text-neutral-500">
                  {article.word_count ? `${article.word_count} words` : "Snippet only"}
                </p>
                {article.summary ? (
                  <p className="mt-2 text-sm leading-6 text-neutral-600">
                    {article.summary}
                  </p>
                ) : null}
              </div>
            ))}
          </div>
        </div>
      </aside>
    </main>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
