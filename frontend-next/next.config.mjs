import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

/** @type {import('next').NextConfig} */
const nextConfig = {
  // typedRoutes moved from experimental to stable in Next.js 15
  typedRoutes: true,
  async rewrites() {
    const apiBase = process.env.API_PROXY_TARGET || "http://localhost:9083";
    const monitoringWs =
      process.env.MONITORING_WS_URL || "http://localhost:9085";
    const terminalWs = process.env.TERMINAL_WS_URL || "http://localhost:9084";
    return [
      {
        source: "/api/backend/:path*",
        destination: `${apiBase}/:path*`,
      },
      {
        source: "/ws/:path*",
        destination: `${monitoringWs}/:path*`,
      },
      {
        source: "/terminal/:path*",
        destination: `${terminalWs}/:path*`,
      },
    ];
  },
  // Development-only: Allow access from LAN IPs to prevent warning
  ...(process.env.NODE_ENV === "development" && {
    experimental: {
      allowedDevOrigins: process.env.DEV_ALLOWED_ORIGINS
        ? process.env.DEV_ALLOWED_ORIGINS.split(",")
        : [
            "localhost:9081",
            "127.0.0.1:9081",
            // Allow common private network ranges
            ...(process.env.ALLOW_LAN === "true"
              ? [
                  // 192.168.x.x (most common home networks)
                  /^192\.168\.\d{1,3}\.\d{1,3}:9081$/,
                  // 10.x.x.x (corporate networks)
                  /^10\.\d{1,3}\.\d{1,3}\.\d{1,3}:9081$/,
                  // 172.16.x.x - 172.31.x.x (docker, corporate)
                  /^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}:9081$/,
                ]
              : []),
          ],
    },
  }),
};

export default withNextIntl(nextConfig);
