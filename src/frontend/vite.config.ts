import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";
import { defineConfig, loadEnv } from "vite";

function readBooleanEnv(rawValue: string | undefined, fallback: boolean): boolean {
  if (!rawValue) {
    return fallback;
  }

  const normalizedValue = rawValue.trim().toLowerCase();

  if (["1", "true", "yes", "on"].includes(normalizedValue)) {
    return true;
  }

  if (["0", "false", "no", "off"].includes(normalizedValue)) {
    return false;
  }

  return fallback;
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const sourceMapsEnabled = readBooleanEnv(env.VITE_OBSERVABILITY_SOURCEMAPS_ENABLED, false);

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./", import.meta.url)),
        "@/app": fileURLToPath(new URL("./app", import.meta.url)),
        "@/pages": fileURLToPath(new URL("./pages", import.meta.url)),
        "@/features": fileURLToPath(new URL("./features", import.meta.url)),
        "@/entities": fileURLToPath(new URL("./entities", import.meta.url)),
        "@/shared": fileURLToPath(new URL("./shared", import.meta.url)),
      },
    },
    build: {
      sourcemap: sourceMapsEnabled ? "hidden" : false,
    },
    server: {
      host: "0.0.0.0",
      port: 5173,
    },
    test: {
      environment: "jsdom",
      globals: true,
      setupFiles: ["./tests/setup/vitest.setup.ts"],
    },
  };
});
