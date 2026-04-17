import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: "/coacher_v1_setup.exe",
        headers: [
          {
            key: "Content-Type",
            value: "application/vnd.microsoft.portable-executable",
          },
          {
            key: "Content-Disposition",
            value: 'attachment; filename="coacher_v1_setup.exe"',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
