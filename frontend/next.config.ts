import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    unoptimized: true, // Recommended for free tier to avoid optimization limits
  },
};

export default nextConfig;
