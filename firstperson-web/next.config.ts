import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  compiler: {
    reactCompiler: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: "/api/:path*",
          destination: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api/:path*",
        },
      ],
    };
  },
};

export default nextConfig;
