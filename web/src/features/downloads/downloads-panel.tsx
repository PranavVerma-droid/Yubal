import type { Job } from "@/api/jobs";
import { EmptyState } from "@/components/common/empty-state";
import { Panel, PanelContent, PanelHeader } from "@/components/common/panel";
import { isActive } from "@/lib/job-status";
import { DownloadIcon, InboxIcon } from "lucide-react";
import { JobCard } from "./job-card";

interface DownloadsPanelProps {
  jobs: Job[];
  onCancel: (jobId: string) => void;
  onDelete: (jobId: string) => void;
}

export function DownloadsPanel({
  jobs,
  onCancel,
  onDelete,
}: DownloadsPanelProps) {
  return (
    <Panel>
      <PanelHeader
        leadingIcon={<DownloadIcon size={18} />}
        badge={
          jobs.length > 0 && (
            <span className="text-foreground-400 font-mono text-xs">
              ({jobs.length})
            </span>
          )
        }
      >
        Downloads
      </PanelHeader>
      <PanelContent height="h-124" className="space-y-2">
        {jobs.length === 0 ? (
          <EmptyState icon={InboxIcon} title="No downloads yet" />
        ) : (
          <div className="flex flex-col gap-2">
            {jobs.map((job) => (
              <JobCard
                job={job}
                onCancel={isActive(job.status) ? onCancel : undefined}
                onDelete={!isActive(job.status) ? onDelete : undefined}
              />
            ))}
          </div>
        )}
      </PanelContent>
    </Panel>
  );
}
