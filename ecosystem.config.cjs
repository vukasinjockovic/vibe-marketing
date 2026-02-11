const { readFileSync } = require('fs');
const { resolve } = require('path');

// Load .env file
const envPath = resolve(__dirname, '.env');
const envVars = {};
try {
  readFileSync(envPath, 'utf-8')
    .split('\n')
    .filter((line) => line && !line.startsWith('#'))
    .forEach((line) => {
      const [key, ...rest] = line.split('=');
      if (key && rest.length) envVars[key.trim()] = rest.join('=').trim();
    });
} catch (_) {
  // .env not found — use defaults
}

module.exports = {
  apps: [
    {
      name: 'vibe-dashboard',
      cwd: './dashboard',
      script: 'node',
      args: '.output/server/index.mjs',
      env: {
        PORT: 3000,
        HOST: '127.0.0.1',
        NODE_ENV: 'production',
        NUXT_PUBLIC_CONVEX_URL: envVars.NUXT_PUBLIC_CONVEX_URL || 'http://localhost:3210',
      },
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 3000,
      max_memory_restart: '512M',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: '../logs/dashboard-error.log',
      out_file: '../logs/dashboard-out.log',
      merge_logs: true,
    },
  ],
};
