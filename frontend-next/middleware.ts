import createMiddleware from "next-intl/middleware";
import { NextRequest, NextResponse } from "next/server";
import { defaultLocale, localePrefix, locales } from "./src/i18n/config";

const intlMiddleware = createMiddleware({
  locales,
  defaultLocale,
  localePrefix,
});

/**
 * Admin-only routes that require admin role
 */
const ADMIN_ONLY_ROUTES = [
  "/users",
  "/settings/domain",
  "/settings/email",
];

/**
 * Check if route requires admin access
 */
function isAdminRoute(pathname: string): boolean {
  // Remove locale prefix to check route
  const pathWithoutLocale = pathname.replace(/^\/(en|vi|fr|es|de|ja|ko|zh-CN)/, "");
  return ADMIN_ONLY_ROUTES.some(route => pathWithoutLocale.startsWith(route));
}

export default async function middleware(request: NextRequest) {
  const intlResponse = intlMiddleware(request);
  const { pathname } = request.nextUrl;

  const isApiRoute = pathname.startsWith("/api/");
  const isStatic =
    pathname.startsWith("/_next") ||
    pathname.startsWith("/assets") ||
    pathname.match(/\.(.*)$/);
  const isLogin = pathname.endsWith("/login");
  const isAccessDenied = pathname.endsWith("/access-denied");

  // Security: Remove credentials from URL if present on login page
  if (isLogin) {
    const url = request.nextUrl;
    const hasCredentials = 
      url.searchParams.has("username") || 
      url.searchParams.has("password") ||
      url.searchParams.has("user") ||
      url.searchParams.has("pass") ||
      url.searchParams.has("pwd");
    
    if (hasCredentials) {
      // Redirect to clean URL
      url.searchParams.delete("username");
      url.searchParams.delete("password");
      url.searchParams.delete("user");
      url.searchParams.delete("pass");
      url.searchParams.delete("pwd");
      return NextResponse.redirect(url);
    }
  }

  if (isApiRoute || isStatic) {
    return intlResponse;
  }

  const segments = pathname.split("/");
  const locale = locales.includes(segments[1]) ? segments[1] : defaultLocale;
  const token = request.cookies.get("auth_token")?.value;

  // When unauthenticated, check if first-run setup is required; redirect to setup
  if (!token && !isLogin && !isAccessDenied) {
    try {
      const statusUrl = new URL("/api/proxy/api/setup/status", request.url);
      const statusRes = await fetch(statusUrl, { cache: "no-store" });
      if (statusRes.ok) {
        const { needs_setup } = await statusRes.json();
        const alreadyOnSetup = pathname.endsWith("/setup");
        if (needs_setup && !alreadyOnSetup) {
          const setupUrl = request.nextUrl.clone();
          setupUrl.pathname = `/${locale}/setup`;
          return NextResponse.redirect(setupUrl);
        }
      }
    } catch (e) {
      // Ignore errors and fall back to login
    }

    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = `/${locale}/login`;
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Check for admin-only routes
  if (token && isAdminRoute(pathname) && !isAccessDenied) {
    try {
      // Verify user role by calling session endpoint
      const sessionUrl = new URL("/api/auth/session", request.url);
      const sessionResponse = await fetch(sessionUrl, {
        headers: {
          Cookie: `auth_token=${token}`,
        },
        cache: "no-store",
      });

      if (sessionResponse.ok) {
        const sessionData = await sessionResponse.json();
        if (sessionData.authenticated && sessionData.user?.role !== "admin") {
          // User is authenticated but not admin - redirect to access denied
          const deniedUrl = request.nextUrl.clone();
          deniedUrl.pathname = `/${locale}/access-denied`;
          deniedUrl.searchParams.set("from", pathname);
          return NextResponse.redirect(deniedUrl);
        }
      }
    } catch (error) {
      console.error("Error checking user role:", error);
    }
  }

  return intlResponse;
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|manifest.json|icons|robots.txt).*)",
  ],
};
