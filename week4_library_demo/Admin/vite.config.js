import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"), // Định nghĩa alias @ trỏ tới thư mục src
    },
  },
  server: {
    port: 5174, // Bạn có thể đổi port nếu cần
  },
});
