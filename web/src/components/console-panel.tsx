import { ChevronDown, Terminal } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useMemo, useRef } from "react";
import type { components } from "../api/schema";
import { useLocalStorage } from "../hooks/use-local-storage";
import { useLogs } from "../hooks/use-logs";
import { Panel, PanelContent, PanelHeader } from "./common/panel";
import { LogLine } from "./console/log-renderers";

type LogEntry = components["schemas"]["LogEntry"];

type ParsedLine =
  | { type: "json"; entry: LogEntry }
  | { type: "text"; text: string };

function parseLine(line: string): ParsedLine {
  try {
    return { type: "json", entry: JSON.parse(line) };
  } catch {
    return { type: "text", text: line };
  }
}

export function ConsolePanel() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { lines, isConnected } = useLogs();
  const [isExpanded, setIsExpanded] = useLocalStorage(
    "yubal-console-expanded",
    false,
  );

  // Memoize parsed lines to avoid re-parsing on every render
  const parsedLines = useMemo(() => lines.map(parseLine), [lines]);

  // Auto-scroll to bottom when new lines arrive
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [lines]);

  return (
    <Panel>
      <PanelHeader
        className="hover:bg-content2 cursor-pointer select-none"
        onClick={() => setIsExpanded(!isExpanded)}
        leadingIcon={<Terminal size={18} />}
        badge={
          !isConnected && (
            <span className="text-warning text-xs">disconnected</span>
          )
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
      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <PanelContent
              ref={containerRef}
              className="console-logs space-y-0.5 p-4 font-mono text-xs"
            >
              {parsedLines.length === 0 ? (
                <div className="flex h-full items-center justify-center">
                  <span className="text-foreground-400">
                    Awaiting YouTube URL...
                  </span>
                </div>
              ) : (
                <AnimatePresence initial={false}>
                  {parsedLines.map((parsed, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      {parsed.type === "json" ? (
                        <LogLine entry={parsed.entry} />
                      ) : (
                        <div className="text-foreground-400">{parsed.text}</div>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
              )}
            </PanelContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Panel>
  );
}
