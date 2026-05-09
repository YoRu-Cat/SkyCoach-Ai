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
    // CRITICAL: do NOT manually split node_modules into multiple chunks.
    // The previous manualChunks config produced production errors like
    //   "Cannot read properties of undefined (reading 'createContext')"
    // and
    //   "Cannot read properties of undefined (reading 'forwardRef')"
    // because secondary chunks (lucide-react, framer-motion, react-leaflet,
    // etc.) evaluated before React was hydrated into the module scope.
    // Letting Rollup pick its own chunking guarantees React loads first
    // for any chunk that depends on it.
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
});
