import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import SWRegister from "./sw-register";

export const metadata: Metadata = {
  title: "RecallCode AI - Your Lifelong Coding Brain",
  description: "Master coding problems with spaced repetition and AI coaching",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "RecallCode AI",
  },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: "#3b82f6",
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
      </head>
      <body>
        {children}
        <Toaster position="top-right" />
        <SWRegister />
      </body>
    </html>
  );
}

