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
  params: { locale: string };
}) {
  // Enable static rendering for next-intl
  setRequestLocale(params.locale);
  
  const messages = await getMessages();
  return (
    <html lang={params.locale} suppressHydrationWarning>
      <body className="antialiased">
        <AppProviders locale={params.locale} messages={messages}>
          {children}
        </AppProviders>
      </body>
    </html>
  );
}
