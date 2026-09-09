import type { NextConfig } from "next";

const isProduction = process.env.NODE_ENV === "production";

const nextConfig: NextConfig = {
  output: "export",
  basePath: isProduction ? `/${process.env.GITHUB_REPO}` : undefined,
  assetPrefix: isProduction ? `${process.env.GITHUB_URL}${process.env.GITHUB_REPO}` : undefined,
  images: {
    unoptimized: isProduction,
    loader: "custom",
    loaderFile: "./image-loader.js",
  }
};

export default nextConfig;
