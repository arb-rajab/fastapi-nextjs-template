import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output: a self-contained server.js plus only the traced
  // dependencies, used by docker/Dockerfile.prod. It does not affect
  // `next dev` or the dev Dockerfile.
  output: "standalone",
};

export default nextConfig;
