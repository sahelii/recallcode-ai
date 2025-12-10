import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import SWRegister from "./sw-register";

export const metadata: Metadata = {
  title: "RecallCode AI - Your Lifelong Coding Brain",
  description: "Master coding problems with spaced repetition and AI coaching",
  manifest: "/manifest.json",
  themeColor: "#3b82f6",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "RecallCode AI",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <link rel="apple-touch-icon" href="/icon-192.png" />
      </head>
      <body>
        {children}
        <Toaster position="top-right" />
        <SWRegister />
      </body>
    </html>
  );
}

