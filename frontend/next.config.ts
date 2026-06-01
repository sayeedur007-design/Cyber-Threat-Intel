import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Compiles Next.js as a fully static SPA suitable for Cloudflare Pages static asset hosting since all backend communication is client-side.
  output: "export",
  images: {
    unoptimized: true, // Recommended for free tier to avoid optimization limits
  },
};

export default nextConfig;
