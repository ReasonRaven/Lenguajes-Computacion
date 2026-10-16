import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En desarrollo, /api/* se reenvía al backend (Backend-Unificado) sin el prefijo /api.
const BACKEND = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: BACKEND,
        changeOrigin: true,
        rewrite: (ruta) => ruta.replace(/^\/api/, ""),
      },
    },
  },
  preview: {
    proxy: {
      "/api": {
        target: BACKEND,
        changeOrigin: true,
        rewrite: (ruta) => ruta.replace(/^\/api/, ""),
      },
    },
  },
});
