const path = require('path');

module.exports = function override(config, env) {
  // Fix allowedHosts issue
  if (config.devServer) {
    config.devServer.allowedHosts = ['localhost', '.localhost', '127.0.0.1'];
  }
  
  // Ensure proper host binding
  if (env === 'development') {
    config.devServer = {
      ...config.devServer,
      allowedHosts: ['localhost', '.localhost', '127.0.0.1'],
      host: 'localhost',
      port: 3000
    };
  }
  
  return config;
};
