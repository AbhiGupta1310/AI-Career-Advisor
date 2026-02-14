import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/chat": "http://localhost:8000",
      "/predict_profile_type": "http://localhost:8000",
      "/recommend_skills": "http://localhost:8000",
      "/career_advice": "http://localhost:8000",
      "/api": "http://localhost:8000",
    },
  },
});
