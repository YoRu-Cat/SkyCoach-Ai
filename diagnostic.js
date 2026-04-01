#!/usr/bin/env node
/**
 * SkyCoach AI - Full Stack Setup Diagnostic
 * Run this to verify both backend and frontend are working
 */

const http = require("http");

// Colors for terminal output
const colors = {
  reset: "\x1b[0m",
  green: "\x1b[32m",
  red: "\x1b[31m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
};

function checkServer(url, name) {
  return new Promise((resolve) => {
    const checkUrl = new URL(url);
    const options = {
      hostname: checkUrl.hostname,
      port: checkUrl.port,
      path: checkUrl.pathname,
      method: "GET",
      timeout: 5000,
    };

    console.log(`\n${colors.cyan}[*] Testing ${name}...${colors.reset}`);
    console.log(`    URL: ${url}`);

    const req = http.request(options, (res) => {
      console.log(
        `    Status: ${colors.green}${res.statusCode}${colors.reset}`,
      );
      resolve(res.statusCode >= 200 && res.statusCode < 500);
      res.destroy();
    });

    req.on("error", (err) => {
      console.log(`    Status: ${colors.red}ERROR${colors.reset}`);
      console.log(`    Error: ${err.message}`);
      resolve(false);
    });

    req.on("timeout", () => {
      console.log(`    Status: ${colors.red}TIMEOUT${colors.reset}`);
      req.destroy();
      resolve(false);
    });

    req.end();
  });
}

async function runDiagnostics() {
  console.log(
    `\n${colors.blue}╔══════════════════════════════════════════╗${colors.reset}`,
  );
  console.log(
    `${colors.blue}║  SkyCoach AI - Full Stack Diagnostics   ║${colors.reset}`,
  );
  console.log(
    `${colors.blue}╚══════════════════════════════════════════╝${colors.reset}\n`,
  );

  // Test backend
  const backendHealthy = await checkServer(
    "http://localhost:8000/health",
    "Backend API",
  );

  // Test backend API endpoint
  const backendApi = await checkServer(
    "http://localhost:8000/api/health",
    "Backend API Endpoint",
  );

  // Test frontend (gets 404 because Vite serves SPA)
  const frontendHealthy = await checkServer(
    "http://localhost:3000/",
    "Frontend Dev Server",
  );

  console.log(
    `\n${colors.blue}═══════════════════════════════════════════${colors.reset}`,
  );
  console.log(`${colors.blue}RESULTS:${colors.reset}`);
  console.log(
    `${backendHealthy ? colors.green + "✓" : colors.red + "✗"} Backend: http://localhost:8000 ${
      backendHealthy ? colors.green + "RUNNING" : colors.red + "NOT RUNNING"
    }${colors.reset}`,
  );
  console.log(
    `${frontendHealthy ? colors.green + "✓" : colors.red + "✗"} Frontend: http://localhost:3000 ${
      frontendHealthy ? colors.green + "RUNNING" : colors.red + "NOT RUNNING"
    }${colors.reset}`,
  );

  if (backendHealthy && (frontendHealthy || !frontendHealthy)) {
    console.log(`\n${colors.green}✓ YOUR APP IS READY!${colors.reset}`);
    console.log(`\n${colors.yellow}NEXT STEPS:${colors.reset}`);
    console.log(`1. Open your browser: http://localhost:3000`);
    console.log(`2. Try entering an activity (e.g., "washing car")`);
    console.log(`3. Select a city and click "Analyze"`);
    console.log(`4. You should see the AI analysis with weather data`);
  } else {
    console.log(`\n${colors.red}⚠ SETUP INCOMPLETE${colors.reset}`);
    if (!backendHealthy) {
      console.log(`\n${colors.yellow}Backend not running!${colors.reset}`);
      console.log(`In a new terminal, run:`);
      console.log(
        `  cd e:\\Java\\Project\\"Project Ai" && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`,
      );
    }
    if (!frontendHealthy) {
      console.log(`\n${colors.yellow}Frontend is starting...${colors.reset}`);
      console.log(`This can take 30 seconds on first run. Please wait.`);
    }
  }

  console.log(
    `\n${colors.blue}═══════════════════════════════════════════${colors.reset}\n`,
  );
}

runDiagnostics().catch(console.error);
