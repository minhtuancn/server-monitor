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
                  // 192.168.0.0/16 (most common home networks)
                  // Matches 192.168.0.0 - 192.168.255.255
                  /^192\.168\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):9081$/,
                  // 10.0.0.0/8 (corporate networks)
                  // Matches 10.0.0.0 - 10.255.255.255
                  /^10\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):9081$/,
                  // 172.16.0.0/12 (Docker, corporate)
                  // Matches 172.16.0.0 - 172.31.255.255
                  /^172\.(1[6-9]|2[0-9]|3[0-1])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):9081$/,
                ]
              : []),
          ],
    },
  }),
};

export default withNextIntl(nextConfig);
