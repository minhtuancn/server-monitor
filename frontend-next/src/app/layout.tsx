import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Server Monitor Dashboard",
  description: "Multi-server monitoring dashboard with real-time insights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
