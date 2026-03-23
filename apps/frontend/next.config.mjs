/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Reduce stale webpack chunk refs in `next dev` (e.g. "Cannot find module './682.js'")
  // on Windows when .next cache gets out of sync with HMR.
  webpack: (config, { dev }) => {
    if (dev) {
      config.cache = false;
    }
    return config;
  },
};

export default nextConfig;
