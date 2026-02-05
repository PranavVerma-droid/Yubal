import type { components } from "./schema";

export type LogEntry = components["schemas"]["LogEntry"];

export type LogLine = {
  id: string;
  entry: LogEntry;
};
