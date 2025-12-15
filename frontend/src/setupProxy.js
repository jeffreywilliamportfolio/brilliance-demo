const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Only proxy specific API requests to the Flask backend
  app.use(
    ['/research', '/examples', '/limits', '/health'],
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      logLevel: 'silent', // Reduce noise in console
      pathRewrite: {
        '^/': '/', // Keep the path as-is
      },
    })
  );
  
  // Don't proxy anything else - let React dev server handle hot reloads
};
