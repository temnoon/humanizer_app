import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3100,
    host: "127.0.0.1", // Localhost only for security
    proxy: {
      "/api": {
        target: "http://localhost:8100",
        changeOrigin: true,
        secure: false,
        // Don't rewrite the path - keep /api prefix
      },
      // Proxy legacy endpoints without /api prefix
      "/models": {
        target: "http://localhost:8100",
        changeOrigin: true,
        secure: false,
      },
      "/configurations": {
        target: "http://localhost:8100",
        changeOrigin: true,
        secure: false,
      },
      "/transform": {
        target: "http://localhost:8100",
        changeOrigin: true,
        secure: false,
      },
      "/health": {
        target: "http://localhost:8100",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
