import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// /api and /n (business pages) go to FastAPI in dev; in the demo FastAPI serves web/dist (one process).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/n/": "http://127.0.0.1:8000",
    },
  },
});
