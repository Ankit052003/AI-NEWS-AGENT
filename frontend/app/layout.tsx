import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "News Research Agent",
  description: "Autonomous AI news research workspace",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-neutral-50 text-neutral-950">
          <header className="border-b border-neutral-200 bg-white">
            <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
              <Link className="text-base font-semibold text-neutral-950" href="/">
                News Research Agent
              </Link>
              <nav className="flex items-center gap-2 text-sm font-medium">
                <Link
                  className="rounded-md px-3 py-2 text-neutral-600 hover:bg-neutral-100 hover:text-neutral-950"
                  href="/reports"
                >
                  Reports
                </Link>
                <Link
                  className="rounded-md px-3 py-2 text-neutral-600 hover:bg-neutral-100 hover:text-neutral-950"
                  href="/dashboard"
                >
                  Dashboard
                </Link>
              </nav>
            </div>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
