import type { Metadata } from "next";
import { Suspense } from "react";
import { DM_Sans, Playfair_Display } from "next/font/google";
import { Footer } from "@/components/Footer";
import { SiteHeader, SiteHeaderFallback } from "@/components/SiteHeader";
import "./globals.css";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-sans-fallback",
  weight: ["400", "500", "600", "700"],
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-serif-fallback",
  weight: ["600", "700"],
});

export const metadata: Metadata = {
  title: "Weekly Product Pulse and Fee Explainer",
  description:
    "INDmoney Play Store reviews → weekly pulse + Exit Load fee explainer",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${dmSans.className} ${playfair.variable}`}>
        <Suspense fallback={<SiteHeaderFallback />}>
          <SiteHeader />
        </Suspense>
        <div className="page-wrap">{children}</div>
        <Footer />
      </body>
    </html>
  );
}
