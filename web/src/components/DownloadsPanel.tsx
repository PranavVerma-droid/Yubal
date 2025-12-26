import { Card, CardBody, CardHeader } from "@heroui/react";
import { Download } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import type { Job } from "../api/jobs";
import { JobCard } from "./JobCard";

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
  // Split jobs into active (queue) and completed (history)
  const activeJobs = jobs.filter((job) =>
    ["pending", "fetching_info", "downloading", "importing"].includes(
      job.status
    )
  );
  const completedJobs = jobs.filter((job) =>
    ["completed", "failed", "cancelled"].includes(job.status)
  );

  return (
    <Card className="border-default-200 flex flex-col overflow-hidden border">
      <CardHeader className="border-default-200 shrink-0 border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <Download className="text-default-500 h-4 w-4" />
          <span className="text-default-500 font-mono text-xs tracking-wider uppercase">
            Downloads
          </span>
          {jobs.length > 0 && (
            <span className="text-default-400 font-mono text-xs">
              {jobs.length}
            </span>
          )}
        </div>
      </CardHeader>
      <CardBody className="h-72 space-y-2 overflow-y-auto p-3">
        {jobs.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <p className="text-default-400/50 font-mono text-xs">
              No downloads yet
            </p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {activeJobs.map((job) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <JobCard job={job} onCancel={onCancel} />
              </motion.div>
            ))}
            {completedJobs.map((job) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                transition={{ duration: 0.2 }}
              >
                <JobCard job={job} onDelete={onDelete} />
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </CardBody>
    </Card>
  );
}
