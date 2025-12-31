import { execSync } from "child_process";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

function getVersion(): string {
  if (process.env.VITE_VERSION) return process.env.VITE_VERSION;
  try {
    return execSync("git describe --tags --always", {
      encoding: "utf-8",
    }).trim();
  } catch {
    return "dev";
  }
}

export default defineConfig({
  define: {
    __VERSION__: JSON.stringify(getVersion()),
  },
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
