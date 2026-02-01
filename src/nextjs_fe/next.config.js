const nextConfig = {
  /* config options here */
  reactStrictMode: true,
  output: 'standalone',
  compress: false,
  async rewrites() {
    return [
      {
        source: '/api/:path((?!auth/).*)',
        destination: 'http://127.0.0.1:8000/:path',
      },
      {
        source: '/api',
        destination: 'http://127.0.0.1:8000/',
      }
    ];
  },
};

module.exports = nextConfig;
