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
};

export default withNextIntl(nextConfig);
