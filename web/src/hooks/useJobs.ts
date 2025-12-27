import { useState, useCallback, useRef, useEffect } from "react";
import {
  createJob,
  listJobs,
  cancelJob as cancelJobApi,
  type Job,
  type JobStatus,
  type AlbumInfo,
} from "../api/jobs";

export type { JobStatus } from "../api/jobs";

export interface LogEntry {
  id: number;
  timestamp: Date;
  step: JobStatus;
  message: string;
}

export interface UseJobsResult {
  // Current job state
  currentJobId: string | null;
  status: JobStatus;
  progress: number;
  logs: LogEntry[];
  albumInfo: AlbumInfo | null;
  error: string | null;

  // Actions
  startJob: (url: string, audioFormat?: string) => Promise<void>;
  stopPolling: () => void;
  clearCurrentJob: () => void;
  cancelJob: (jobId: string) => Promise<void>;

  // Job list
  jobs: Job[];
  refreshJobs: () => Promise<void>;
  resumeJob: (jobId: string) => void;
}

const POLL_INTERVAL = 2000; // 2 seconds

export function useJobs(): UseJobsResult {
  // Current job state (for console display)
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<JobStatus>("idle");
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [albumInfo, setAlbumInfo] = useState<AlbumInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Job list
  const [jobs, setJobs] = useState<Job[]>([]);

  // Refs
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const logIdRef = useRef(0);
  const lastMessageRef = useRef<string>("");
  const isPollingRef = useRef(false);

  const addLog = useCallback((step: JobStatus, message: string) => {
    // Skip if same message as last logged
    if (message === lastMessageRef.current) return;
    lastMessageRef.current = message;

    logIdRef.current += 1;
    setLogs((prev) => [
      ...prev,
      {
        id: logIdRef.current,
        timestamp: new Date(),
        step,
        message,
      },
    ]);
  }, []);

  const resetState = useCallback(() => {
    setStatus("idle");
    setProgress(0);
    setLogs([]);
    setAlbumInfo(null);
    setError(null);
    logIdRef.current = 0;
    lastMessageRef.current = "";
  }, []);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const startPolling = useCallback(() => {
    if (isPollingRef.current) return;
    isPollingRef.current = true;
    stopPolling();

    const poll = async () => {
      const { jobs: jobList } = await listJobs();
      setJobs(jobList);

      // Check if there are any active jobs
      const hasActiveJobs = jobList.some(
        (j) => !["completed", "failed", "cancelled"].includes(j.status)
      );

      // Stop polling if no active jobs
      if (!hasActiveJobs) {
        stopPolling();
        isPollingRef.current = false;
      }
    };

    // Poll immediately, then at interval
    poll();
    pollingRef.current = setInterval(poll, POLL_INTERVAL);
  }, [stopPolling]);

  // Update current job state when jobs change
  useEffect(() => {
    if (!currentJobId) return;
    const job = jobs.find((j) => j.id === currentJobId);
    if (!job) return;

    setStatus(job.status);
    setProgress(job.progress);

    if (job.album_info) {
      setAlbumInfo(job.album_info);
    }

    if (job.message && job.message !== lastMessageRef.current) {
      lastMessageRef.current = job.message;
      addLog(job.status, job.message);
    }

    if (job.error) {
      setError(job.error);
    }
  }, [jobs, currentJobId, addLog]);

  const startJob = useCallback(
    async (url: string, audioFormat = "mp3") => {
      resetState();
      setStatus("pending");
      addLog("pending", `Creating job for: ${url}`);

      const result = await createJob(url, audioFormat);

      if (!result.success) {
        setStatus("failed");
        setError(result.error);
        addLog("failed", result.error);
        return;
      }

      setCurrentJobId(result.jobId);
      addLog("pending", `Job created: ${result.jobId}`);

      // Refresh job list to show the new job immediately
      const { jobs: jobList } = await listJobs();
      setJobs(jobList);

      startPolling();
    },
    [addLog, resetState, startPolling]
  );

  const clearCurrentJob = useCallback(() => {
    stopPolling();
    setCurrentJobId(null);
    resetState();
  }, [resetState, stopPolling]);

  const refreshJobs = useCallback(async () => {
    const { jobs: jobList, activeJobId } = await listJobs();
    setJobs(jobList);

    // Check if there are any active jobs
    const hasActiveJobs = jobList.some(
      (j) => !["completed", "failed", "cancelled"].includes(j.status)
    );

    // Auto-resume active job if we're not tracking any
    if (activeJobId && !currentJobId) {
      const activeJob = jobList.find((j) => j.id === activeJobId);
      if (
        activeJob &&
        !["completed", "failed", "cancelled"].includes(activeJob.status)
      ) {
        // Resume the active job
        setCurrentJobId(activeJobId);
        setStatus(activeJob.status);
        setProgress(activeJob.progress);
        if (activeJob.album_info) {
          setAlbumInfo(activeJob.album_info);
        }

        // Load existing logs
        const newLogs = activeJob.logs.map((log, i) => ({
          id: i + 1,
          timestamp: new Date(log.timestamp),
          step: log.step as JobStatus,
          message: log.message,
        }));
        setLogs(newLogs);
        logIdRef.current = newLogs.length;
      }
    }

    // Start polling if there are active jobs
    if (hasActiveJobs) {
      startPolling();
    }
  }, [currentJobId, startPolling]);

  const cancelJob = useCallback(
    async (jobId: string) => {
      await cancelJobApi(jobId);
      // If cancelling current job, stop polling and update status
      if (jobId === currentJobId) {
        stopPolling();
        setStatus("cancelled");
        addLog("cancelled", "Job cancelled by user");
      }
      // Refresh the job list to get updated statuses
      const { jobs: jobList } = await listJobs();
      setJobs(jobList);
    },
    [currentJobId, stopPolling, addLog]
  );

  const resumeJob = useCallback(
    (jobId: string) => {
      const job = jobs.find((j) => j.id === jobId);
      if (!job) return;

      resetState();
      setCurrentJobId(jobId);
      setStatus(job.status);
      setProgress(job.progress);
      if (job.album_info) {
        setAlbumInfo(job.album_info);
      }
      if (job.error) {
        setError(job.error);
      }

      // Load existing logs
      const newLogs = job.logs.map((log, i) => ({
        id: i + 1,
        timestamp: new Date(log.timestamp),
        step: log.step as JobStatus,
        message: log.message,
      }));
      setLogs(newLogs);
      logIdRef.current = newLogs.length;

      // If job is still running, start polling
      if (!["completed", "failed", "cancelled"].includes(job.status)) {
        startPolling();
      }
    },
    [jobs, resetState, startPolling]
  );

  // Refresh jobs on mount and check for active job
  useEffect(() => {
    refreshJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    currentJobId,
    status,
    progress,
    logs,
    albumInfo,
    error,
    startJob,
    stopPolling,
    clearCurrentJob,
    cancelJob,
    jobs,
    refreshJobs,
    resumeJob,
  };
}
