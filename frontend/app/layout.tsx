import type { Metadata } from "next";
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
      <body>{children}</body>
    </html>
  );
}
