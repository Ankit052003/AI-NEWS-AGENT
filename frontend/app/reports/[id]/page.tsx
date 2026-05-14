import { ReportDetail } from "@/components/ReportDetail";

type ReportDetailPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function ReportDetailPage({
  params,
}: ReportDetailPageProps) {
  const { id } = await params;
  return <ReportDetail reportId={id} />;
}
