import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Eli OS — Growth Command Center",
  description: "VirtuaLab Digital's AI growth intelligence platform. Eli is the daughter of Joseph — your command center for SEO, content, campaigns, and business growth automation.",
  keywords: ["Eli OS", "VirtuaLab", "AI", "Growth", "SEO", "Command Center", "Intelligence"],
  icons: {
    icon: "https://z-cdn.chatglm.cn/z-ai/static/logo.svg",
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
        <Toaster />
      </body>
    </html>
  );
}
