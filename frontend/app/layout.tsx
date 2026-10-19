import "./globals.css";
import React from "react";

export const metadata = {
  title: "NeuroSymbolic AI | Interpretable Decision Support",
  description: "A Hybrid Symbolic-Neural Framework for Multi-Agent Decision Intelligence",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <header className="bg-navy-900 text-white border-b border-navy-800 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-navy-600 flex items-center justify-center font-bold text-lg text-white">
              NS
            </div>
            <div>
              <h1 className="font-semibold text-lg leading-tight">NeuroSymbolic Decision Platform</h1>
              <p className="text-xs text-slate-400">Interpretable Multi-Agent Decision Support Framework</p>
            </div>
          </div>
          <nav className="flex items-center space-x-6 text-sm font-medium text-slate-300">
            <a href="/" className="hover:text-white transition">Overview</a>
            <a href="/decision" className="hover:text-white transition">Decision Analysis</a>
            <a href="/chat" className="hover:text-white transition">AI Workspace</a>
            <a href="/evaluations" className="hover:text-white transition">Research Benchmark</a>
            <a href="/rules" className="hover:text-white transition">Rules Registry</a>
            <a href="/audit" className="hover:text-white transition">Audit Trail</a>
          </nav>
        </header>
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          {children}
        </main>
        <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500">
          Ballari Institute of Technology and Management (BITM) &bull; Project Work Phase-1 &bull; Candidate: Anjana Priya (3BR25MC009)
        </footer>
      </body>
    </html>
  );
}
