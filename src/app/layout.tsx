import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Eli — AI Growth Intelligence | VirtuaLab Digital",
  description:
    "VirtuaLab Digital's AI-powered growth intelligence platform. Ask Eli about SEO strategy, keyword research, content optimization, competitive analysis, and automation workflows.",
 keywords: [
    "AI SEO",
    "Growth Intelligence",
    "Keyword Research",
    "Content Strategy",
    "SEO Automation",
    "MicroSaaS",
    "E-E-A-T Content",
    "VirtuaLab Digital",
    "AI Agent",
  ],
  authors: [{ name: "VirtuaLab Digital", url: "https://virtualabdigital.com" }],
  creator: "VirtuaLab Digital",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    title: "Eli — AI Growth Intelligence | VirtuaLab Digital",
    description:
      "AI-powered growth intelligence. Ask Eli about SEO strategy, keyword research, content optimization, and automation workflows.",
    url: "https://eli.virtualabdigital.com",
    siteName: "Eli by VirtuaLab Digital",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Eli — AI Growth Intelligence | VirtuaLab Digital",
    description:
      "AI-powered growth intelligence. Ask Eli about SEO strategy, keyword research, content optimization, and automation workflows.",
  },
  icons: {
    icon: "/logo.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased bg-[#f8fafc] text-[#1e293b]`}>
        {children}
        <footer className="text-center py-3 text-[11px] text-[#94a3b8] border-t border-[#e2e8f0] bg-white">
          &copy; {new Date().getFullYear()}{" "}
          <a
            href="https://virtualabdigital.com"
            className="hover:text-[#7c3aed] transition-colors"
            target="_blank"
            rel="noopener noreferrer"
          >
            VirtuaLab Digital
          </a>{" "}
          &mdash; Eli MicroSaaS
        </footer>
      </body>
    </html>
  );
}
