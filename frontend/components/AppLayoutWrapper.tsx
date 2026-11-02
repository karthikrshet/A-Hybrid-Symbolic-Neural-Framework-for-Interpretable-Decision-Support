'use client';
import React from 'react';
import { usePathname } from 'next/navigation';
import { FiMessageSquare } from 'react-icons/fi';

export default function AppLayoutWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isChatPage = pathname === '/chat';

  if (isChatPage) {
    return (
      <div className="h-screen w-screen overflow-hidden bg-white flex">
        {children}
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <header className="bg-navy-900 text-white border-b border-navy-800 px-6 py-3.5 flex items-center justify-between sticky top-0 z-50 shadow-md">
        <div className="flex items-center space-x-3">
          <a href="/" className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-navy-600 flex items-center justify-center font-bold text-base text-white shadow-inner">
              NS
            </div>
            <div>
              <h1 className="font-bold text-sm tracking-tight leading-tight">NeuroSymbolic AI</h1>
              <p className="text-[10px] text-slate-400 font-mono">Decision Intelligence</p>
            </div>
          </a>
        </div>
        <nav className="flex items-center space-x-4 text-xs font-medium text-slate-300">
          <a href="/" className="hover:text-white transition">Overview</a>
          <a href="/chat" className="px-2.5 py-1 bg-navy-700 hover:bg-navy-600 text-white rounded font-semibold transition flex items-center space-x-1.5 shadow-sm">
            <FiMessageSquare className="w-3.5 h-3.5" />
            <span>AI Chatbot</span>
          </a>
          <a href="/decision" className="hover:text-white transition">Analysis Studio</a>
          <a href="/agents" className="hover:text-white transition">Agents</a>
          <a href="/datasets" className="hover:text-white transition">Datasets</a>
          <a href="/models" className="hover:text-white transition">Models</a>
          <a href="/evaluations" className="hover:text-white transition">Benchmarks</a>
          <a href="/history" className="hover:text-white transition">History</a>
          <a href="/rules" className="hover:text-white transition">Rules</a>
          <a href="/audit" className="hover:text-white transition">Audit</a>
          <a href="/settings" className="hover:text-white transition">Settings</a>
        </nav>
      </header>

      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        {children}
      </main>

      <footer className="border-t border-slate-200 bg-white py-3 px-6 text-center text-xs text-slate-500">
        NeuroSymbolic AI Decision Support Platform &bull; Production Multi-Agent Intelligence System
      </footer>
    </div>
  );
}
