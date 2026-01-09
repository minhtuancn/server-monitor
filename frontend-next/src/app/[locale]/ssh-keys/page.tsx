import { redirect } from "next/navigation";

export default function Page({ params }: { params: { locale: string } }) {
  const { locale } = params;
  redirect(`/${locale}/settings/ssh-keys`);
}
