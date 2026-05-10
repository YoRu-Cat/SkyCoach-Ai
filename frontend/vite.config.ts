import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@pages": path.resolve(__dirname, "./src/pages"),
      "@hooks": path.resolve(__dirname, "./src/hooks"),
      "@services": path.resolve(__dirname, "./src/services"),
      "@utils": path.resolve(__dirname, "./src/utils"),
      "@types": path.resolve(__dirname, "./src/types"),
      "@styles": path.resolve(__dirname, "./src/styles"),
    },
  },
  server: {
    port: 3000,
    strictPort: false,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "/api"),
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    // Rollup decides chunking automatically based on the import graph.
    // This keeps React loaded before any chunk that depends on it; manual
    // chunk splits would otherwise break libraries that consume React's
    // context API (react-query, framer-motion, lucide-react, etc.).
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
});
