import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "OMNISKILL — Universal AI Agent & Skills Framework",
    template: "%s | OMNISKILL",
  },
  description:
    "Discover, install, and orchestrate 49 AI agent skills across 5 platforms. One repo, one format, every platform.",
  metadataBase: new URL("https://omniskill.dev"),
  openGraph: {
    title: "OMNISKILL — Universal AI Agent & Skills Framework",
    description:
      "Discover, install, and orchestrate 49 AI agent skills across 5 platforms. One repo, one format, every platform.",
    siteName: "OMNISKILL",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "OMNISKILL — Universal AI Agent & Skills Framework",
    description: "49 skills, 8 agents, 5 pipelines — one universal framework.",
  },
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-brand-bg text-brand-text antialiased min-h-screen font-sans">
        <Navbar />
        <main className="pt-16">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
