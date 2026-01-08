import Shell from "@/components/layout/Shell";

// Opt out of static generation for routes that use dynamic features
export const dynamic = 'force-dynamic';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <Shell>{children}</Shell>;
}
