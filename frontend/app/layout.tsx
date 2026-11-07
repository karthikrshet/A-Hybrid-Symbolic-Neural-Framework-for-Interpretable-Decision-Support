import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "NeuroSymbolic AI — Interpretable Multi-Agent Decision Support",
  description: "A Hybrid Symbolic-Neural Framework for Interpretable Decision Support across healthcare, finance, cyber security, IT and education.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white font-sans text-ink antialiased">{children}</body>
    </html>
  );
}
