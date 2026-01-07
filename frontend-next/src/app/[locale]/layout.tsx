import { AppProviders } from "@/components/providers/AppProviders";
import { locales } from "@/i18n/config";
import type { Metadata } from "next";
import { getMessages } from "next-intl/server";
import { Geist, Geist_Mono } from "next/font/google";
import "../globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Server Monitor Dashboard",
  description:
    "Modern dashboard for multi-server monitoring, terminal access, and configuration",
};

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const messages = await getMessages();
  return (
    <html lang={params.locale} suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AppProviders locale={params.locale} messages={messages}>
          {children}
        </AppProviders>
      </body>
    </html>
  );
}
