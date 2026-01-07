import { getRequestConfig } from "next-intl/server";
import { defaultLocale, locales } from "./config";
import fs from "node:fs";
import path from "node:path";

const LOCALES_DIR = path.join(process.cwd(), "src", "locales");

function loadMessages(locale: string) {
  const localeFile = path.join(LOCALES_DIR, `${locale}.json`);
  if (fs.existsSync(localeFile)) {
    const content = fs.readFileSync(localeFile, "utf-8");
    return JSON.parse(content);
  }
  const fallback = path.join(LOCALES_DIR, `${defaultLocale}.json`);
  const content = fs.readFileSync(fallback, "utf-8");
  return JSON.parse(content);
}

export default getRequestConfig(async ({ locale }) => {
  const normalizedLocale = locales.includes(locale) ? locale : defaultLocale;
  return {
    locale: normalizedLocale,
    messages: loadMessages(normalizedLocale),
  };
});
