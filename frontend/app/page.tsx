const exampleQueries = [
  "Latest AI startup funding news this week",
  "Recent acquisitions in the AI industry",
  "Funding trends in AI healthcare startups",
];

export default function Home() {
  return (
    <main className="min-h-screen bg-stone-50 px-6 py-10 text-stone-950">
      <section className="mx-auto grid min-h-[calc(100vh-5rem)] max-w-6xl content-center gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-6">
          <div className="space-y-3">
            <p className="text-sm font-medium uppercase tracking-[0.18em] text-teal-700">
              Research workspace
            </p>
            <h1 className="max-w-3xl text-4xl font-semibold leading-tight sm:text-5xl">
              News Research Agent
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-stone-700">
              Start with a focused query, collect reliable sources, and prepare
              the foundation for source-backed market research reports.
            </p>
          </div>

          <form className="space-y-4 rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
            <label
              className="block text-sm font-medium text-stone-700"
              htmlFor="query"
            >
              Research query
            </label>
            <textarea
              className="min-h-32 w-full resize-none rounded-md border border-stone-300 px-4 py-3 text-base outline-none transition focus:border-teal-600 focus:ring-4 focus:ring-teal-100"
              id="query"
              name="query"
              placeholder="Give me the latest AI startup funding news this week."
            />
            <button
              className="rounded-md bg-teal-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-800"
              type="button"
            >
              Prepare Research
            </button>
          </form>
        </div>

        <aside className="self-center rounded-lg border border-stone-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold text-stone-950">
            Example queries
          </h2>
          <div className="mt-4 space-y-3">
            {exampleQueries.map((query) => (
              <p
                className="rounded-md border border-stone-200 bg-stone-50 px-4 py-3 text-sm leading-6 text-stone-700"
                key={query}
              >
                {query}
              </p>
            ))}
          </div>
        </aside>
      </section>
    </main>
  );
}
