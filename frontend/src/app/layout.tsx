import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Deep Insights Copilot | Institutional Intelligence",
  description: "Enterprise-grade AI Copilot for Corporate Banking Analytics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@700;800&display=swap" rel="stylesheet" />
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
      </head>
      <body className={`bg-surface font-body text-on-surface antialiased`}>
        {children}
      </body>
    </html>
  );
}
