import { AppProviders } from "@/components/providers/AppProviders";
import { locales } from "@/i18n/config";
import type { Metadata } from "next";
import { getMessages, setRequestLocale } from "next-intl/server";
import "../globals.css";

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
  params: Promise<{ locale: string }>;
}) {
  // Await the params in Next.js 15+
  const { locale } = await params;
  
  // Enable static rendering for next-intl
  setRequestLocale(locale);
  
  const messages = await getMessages();
  return (
    <AppProviders locale={locale} messages={messages}>
      {children}
    </AppProviders>
  );
}
