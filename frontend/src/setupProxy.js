const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: process.env.REACT_APP_API_URL || 'http://localhost:8001',
      changeOrigin: true,
      pathRewrite: {
        '^/api': '', // remove /api prefix
      },
    })
  );
};
