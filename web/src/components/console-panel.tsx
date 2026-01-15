import { ChevronDown, Terminal } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useRef } from "react";
import type { Job } from "../hooks/use-jobs";
import { useLocalStorage } from "../hooks/use-local-storage";
import { useLogs } from "../hooks/use-logs";
import { isActive } from "../lib/job-status";
import { Panel, PanelContent, PanelHeader } from "./common/panel";

interface ConsolePanelProps {
  jobs: Job[];
}

function StatusIndicator({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: "bg-foreground-500",
    fetching_info: "bg-foreground",
    downloading: "bg-primary",
    importing: "bg-secondary",
    completed: "bg-success",
    failed: "bg-danger",
    cancelled: "bg-warning",
  };
  const color = colors[status] ?? "bg-foreground-500";
  return (
    <span
      className={`inline-flex h-2 w-2 animate-pulse rounded-full ${color}`}
    />
  );
}

export function ConsolePanel({ jobs }: ConsolePanelProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const currentJob = jobs.find((j) => isActive(j.status));
  const { lines, isConnected } = useLogs();
  const [isExpanded, setIsExpanded] = useLocalStorage(
    "yubal-console-expanded",
    false,
  );

  // Auto-scroll to bottom when new lines arrive
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [lines]);

  const panelHeader = (
    <PanelHeader
      className="hover:bg-content2 cursor-pointer select-none"
      onClick={() => setIsExpanded(!isExpanded)}
      leadingIcon={<Terminal size={18} />}
      badge={
        <>
          {currentJob && <StatusIndicator status={currentJob.status} />}
          {!isConnected && (
            <span className="text-warning text-xs">disconnected</span>
          )}
        </>
      }
      trailingIcon={
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="flex items-center justify-center"
        >
          <ChevronDown size={18} />
        </motion.div>
      }
    >
      console
    </PanelHeader>
  );

  const panelContent = (
    <PanelContent
      ref={containerRef}
      className="space-y-0.5 p-4 font-mono text-xs"
    >
      {lines.length === 0 ? (
        <div className="flex h-full items-center justify-center">
          <span className="text-foreground-400">Awaiting YouTube URL...</span>
        </div>
      ) : (
        <AnimatePresence initial={false}>
          {lines.map((line, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className="whitespace-pre-wrap"
              dangerouslySetInnerHTML={{ __html: line }}
            />
          ))}
        </AnimatePresence>
      )}
    </PanelContent>
  );

  return (
    <Panel>
      {panelHeader}
      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            {panelContent}
          </motion.div>
        )}
      </AnimatePresence>
    </Panel>
  );
}
