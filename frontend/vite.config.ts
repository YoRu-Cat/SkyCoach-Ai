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
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return undefined;

          if (id.includes("react-query")) return "query";
          if (id.includes("@tsparticles")) return "particles";
          if (id.includes("leaflet") || id.includes("react-leaflet"))
            return "maps";
          if (
            id.includes("framer-motion") ||
            id.includes("gsap") ||
            id.includes("locomotive-scroll")
          ) {
            return "motion";
          }
          if (id.includes("react") || id.includes("scheduler")) return "vendor";

          return "vendor-misc";
        },
      },
    },
  },
});
