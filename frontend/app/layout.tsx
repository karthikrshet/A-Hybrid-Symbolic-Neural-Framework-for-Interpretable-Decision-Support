import "./globals.css";
import React from "react";
import AppLayoutWrapper from "@/components/AppLayoutWrapper";

export const metadata = {
  title: "NeuroSymbolic AI | Interpretable Decision Support",
  description: "A Hybrid Symbolic-Neural Framework for Multi-Agent Decision Intelligence",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-slate-900 antialiased font-sans">
        <AppLayoutWrapper>
          {children}
        </AppLayoutWrapper>
      </body>
    </html>
  );
}

