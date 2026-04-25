import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Retail Analytics & Forecasting",
  description:
    "Interactive dashboard for time-series forecasting, sales driver analysis, store segmentation, and SHAP explainability.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        <Sidebar />
        <main className="ml-[220px] min-h-screen p-8">{children}</main>
      </body>
    </html>
  );
}
