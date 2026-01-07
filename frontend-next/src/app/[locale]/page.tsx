import { redirect } from "next/navigation";

export default function LocaleHome({ params }: { params: { locale: string } }) {
  redirect(`/${params.locale}/dashboard`);
}
