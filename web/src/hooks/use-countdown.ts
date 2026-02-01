import { useEffect, useState } from "react";

function formatCountdown(targetDate: Date | null): string {
  if (!targetDate) return "—";

  const now = new Date();
  const diff = targetDate.getTime() - now.getTime();

  if (diff <= 0) return "Now";

  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);

  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
  if (minutes > 0) return `${minutes}m ${seconds}s`;
  return `${seconds}s`;
}

export function useCountdown(targetDate: Date | null): string {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (!targetDate) return;

    const interval = setInterval(() => {
      setTick((t) => t + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [targetDate]);

  // Re-compute on each tick or when targetDate changes
  void tick;
  return formatCountdown(targetDate);
}
