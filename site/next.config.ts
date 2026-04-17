import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  images: {
    unoptimized: true,
  },
  // Note: Security headers are managed in render.yaml for static export
};

export default nextConfig;
