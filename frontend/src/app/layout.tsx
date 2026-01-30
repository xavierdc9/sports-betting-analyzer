import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sports Betting Analyzer",
  description: "Real-time odds comparison, arbitrage detection, and value bet analysis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
