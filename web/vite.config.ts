import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// /api and /n (business pages) go to FastAPI in dev; in the demo FastAPI serves web/dist (one process).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Read env files from the repo root (one .env for FastAPI and Vite). Only VITE_* variables reach the browser
  // bundle (Vite's envPrefix), so the server keys in the same file never leak into web/dist.
  envDir: "..",
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/n/": "http://127.0.0.1:8000",
    },
  },
});
