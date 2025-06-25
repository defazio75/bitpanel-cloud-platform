/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      {
        source: '/',
        destination: '/login',
        permanent: false,  // 307 redirect
      },
    ]
  },
}

module.exports = nextConfig
