import { Progress, Skeleton } from "@heroui/react";
import { Music } from "lucide-react";
import { motion } from "framer-motion";
import type { ProgressStep } from "../hooks/useSync";

// TODO: Wire to backend when album metadata is available in SSE events
export interface TrackInfo {
  title: string;
  artist: string;
  album: string;
  artworkUrl?: string;
}

interface AlbumInfoCardProps {
  trackInfo: TrackInfo | null;
  progress: number;
  status: ProgressStep;
}

const progressColors: Record<
  ProgressStep,
  "default" | "primary" | "secondary" | "success" | "warning" | "danger"
> = {
  idle: "default",
  starting: "primary",
  downloading: "primary",
  tagging: "secondary",
  complete: "success",
  error: "danger",
};

export function AlbumInfoCard({
  trackInfo,
  progress,
  status,
}: AlbumInfoCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="bg-default-50 mb-4 rounded-lg border border-white/10 p-4"
    >
      <div className="flex gap-4">
        {/* Album Art */}
        <div className="bg-default-100 flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-md">
          {trackInfo?.artworkUrl ? (
            <img
              src={trackInfo.artworkUrl}
              alt="Album art"
              className="h-full w-full object-cover"
            />
          ) : (
            <Music className="text-default-400 h-6 w-6" />
          )}
        </div>

        {/* Track Info & Progress */}
        <div className="min-w-0 flex-1">
          {trackInfo ? (
            <>
              <p className="text-foreground truncate font-mono text-sm font-medium">
                {trackInfo.title}
              </p>
              <p className="text-default-500 truncate font-mono text-xs">
                {trackInfo.artist}
              </p>
              <p className="text-default-500 truncate font-mono text-xs">
                {trackInfo.album}
              </p>
            </>
          ) : (
            <>
              <Skeleton className="mb-1 h-4 w-32 rounded" />
              <Skeleton className="mb-1 h-3 w-24 rounded" />
              <Skeleton className="h-3 w-24 rounded" />
            </>
          )}

          <div className="mt-3 flex items-center gap-3">
            <Progress
              aria-label="Download progress"
              value={progress}
              color={progressColors[status]}
              size="sm"
              className="flex-1"
            />
            <span className="text-default-500 w-10 text-right font-mono text-xs">
              {Math.round(progress)}%
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
