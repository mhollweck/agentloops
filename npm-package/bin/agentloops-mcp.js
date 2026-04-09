#!/usr/bin/env node

const { spawn, execSync } = require("child_process");

function findPython() {
  for (const cmd of ["python3", "python"]) {
    try {
      const version = execSync(`${cmd} --version 2>&1`, {
        encoding: "utf-8",
      }).trim();
      const match = version.match(/Python (\d+)\.(\d+)/);
      if (match) {
        const major = parseInt(match[1], 10);
        const minor = parseInt(match[2], 10);
        if (major === 3 && minor >= 10) {
          return cmd;
        }
      }
    } catch {
      // command not found, try next
    }
  }
  return null;
}

function checkAgentLoopsMcp(pythonCmd) {
  try {
    execSync(`${pythonCmd} -c "import agentloops_mcp" 2>&1`, {
      encoding: "utf-8",
    });
    return true;
  } catch {
    return false;
  }
}

function main() {
  const pythonCmd = findPython();

  if (!pythonCmd) {
    console.error("Error: Python 3.10+ is required but was not found.");
    console.error("");
    console.error("Install Python 3.10+ from https://www.python.org/downloads/");
    process.exit(1);
  }

  if (!checkAgentLoopsMcp(pythonCmd)) {
    console.error("Error: agentloops[mcp] Python package is not installed.");
    console.error("");
    console.error("Install it with:");
    console.error("");
    console.error("  pip install agentloops[mcp]");
    console.error("");
    console.error("Then run this command again.");
    process.exit(1);
  }

  const args = process.argv.slice(2);

  const child = spawn(pythonCmd, ["-m", "agentloops_mcp", ...args], {
    stdio: ["inherit", "inherit", "inherit"],
    env: process.env,
  });

  child.on("error", (err) => {
    console.error(`Failed to start agentloops-mcp: ${err.message}`);
    process.exit(1);
  });

  child.on("exit", (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
    } else {
      process.exit(code ?? 1);
    }
  });

  function shutdown(signal) {
    child.kill(signal);
  }

  process.on("SIGTERM", () => shutdown("SIGTERM"));
  process.on("SIGINT", () => shutdown("SIGINT"));
}

main();
