import createMiddleware from "next-intl/middleware";
import { NextRequest, NextResponse } from "next/server";
import { defaultLocale, localePrefix, locales } from "./src/i18n/config";

const intlMiddleware = createMiddleware({
  locales,
  defaultLocale,
  localePrefix,
});

export default function middleware(request: NextRequest) {
  const intlResponse = intlMiddleware(request);
  const { pathname } = request.nextUrl;

  const isApiRoute = pathname.startsWith("/api/");
  const isStatic =
    pathname.startsWith("/_next") ||
    pathname.startsWith("/assets") ||
    pathname.match(/\.(.*)$/);
  const isLogin = pathname.endsWith("/login");

  if (isApiRoute || isStatic) {
    return intlResponse;
  }

  const segments = pathname.split("/");
  const locale = locales.includes(segments[1]) ? segments[1] : defaultLocale;
  const token = request.cookies.get("auth_token")?.value;

  if (!token && !isLogin) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = `/${locale}/login`;
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return intlResponse;
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|manifest.json|icons|robots.txt).*)",
  ],
};
