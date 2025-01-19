/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { isServer }) => {
    // 忽略 langdetect 的文档文件
    config.module.rules.push({
      test: /node_modules\/langdetect\/(LICENSE|README\.md)$/,
      use: 'ignore-loader'
    });

    // 处理 .node 文件
    config.module.rules.push({
      test: /\.node$/,
      use: 'node-loader'
    });

    // 添加 node polyfills
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        util: require.resolve('util/')
      };
    }

    return config;
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8888/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
