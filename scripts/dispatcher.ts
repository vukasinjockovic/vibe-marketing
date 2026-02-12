#!/usr/bin/env npx tsx
/**
 * Campaign Dispatcher Service
 *
 * Lightweight HTTP server on localhost:3211 that receives dispatch requests
 * from Convex internalActions and spawns agent processes on the host.
 *
 * Convex runs in Docker and cannot exec `claude` on the host directly,
 * so this bridge service handles the host-side process spawning.
 *
 * Endpoints:
 *   POST /dispatch        — { taskId, agentName } → invoke-agent.sh
 *   POST /dispatch-branch — { taskId, branches: [{label, agent}], model } → multi-agent claude -p
 *   GET  /health          — { ok: true, queued: N }
 *
 * Run via PM2: pm2 start scripts/dispatcher.ts --name vibe-dispatcher --interpreter "npx tsx"
 */

import { createServer, IncomingMessage, ServerResponse } from "http";
import { spawn } from "child_process";
import { appendFileSync, mkdirSync, existsSync, unlinkSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const PORT = 3212;
const STREAM_DIR = "/tmp/vibe-streams";
const __filename = fileURLToPath(import.meta.url);
const PROJECT_DIR = resolve(dirname(__filename), "..");
const INVOKE_SCRIPT = resolve(PROJECT_DIR, "scripts/invoke-agent.sh");
const LOG_DIR = resolve(PROJECT_DIR, "logs");
const LOG_FILE = resolve(LOG_DIR, "dispatcher.log");

// Ensure logs and stream directories exist
if (!existsSync(LOG_DIR)) {
  mkdirSync(LOG_DIR, { recursive: true });
}
if (!existsSync(STREAM_DIR)) {
  mkdirSync(STREAM_DIR, { recursive: true });
}

let activeProcesses = 0;

function log(msg: string) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  process.stdout.write(line);
  try {
    appendFileSync(LOG_FILE, line);
  } catch {}
}

function spawnAgent(agentName: string, taskId: string): void {
  activeProcesses++;
  log(`DISPATCH agent=${agentName} task=${taskId} (active=${activeProcesses})`);

  const agentLog = resolve(LOG_DIR, `${agentName}-${taskId.slice(-8)}.log`);
  const child = spawn("bash", [INVOKE_SCRIPT, agentName, taskId], {
    cwd: PROJECT_DIR,
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, HOME: process.env.HOME || "/root" },
    detached: true,
  });

  child.stdout?.on("data", (data: Buffer) => {
    try { appendFileSync(agentLog, data); } catch {}
  });
  child.stderr?.on("data", (data: Buffer) => {
    try { appendFileSync(agentLog, data); } catch {}
  });

  child.on("exit", (code) => {
    activeProcesses--;
    log(`COMPLETED agent=${agentName} task=${taskId} exit=${code} (active=${activeProcesses})`);
  });

  child.on("error", (err) => {
    activeProcesses--;
    log(`ERROR agent=${agentName} task=${taskId} err=${err.message}`);
  });

  // Don't let the child keep this process alive
  child.unref();
}

function spawnBranchGroup(
  taskId: string,
  branches: { label: string; agent: string }[],
  model: string
): void {
  activeProcesses++;
  const branchLabels = branches.map((b) => b.label).join(",");
  log(`DISPATCH-BRANCH task=${taskId} branches=[${branchLabels}] model=${model} (active=${activeProcesses})`);

  // Build a prompt that instructs Claude to run each agent sequentially
  const agentInstructions = branches
    .map(
      (b) =>
        `- Run agent "${b.agent}" for branch "${b.label}": ` +
        `Read its SKILL.md from .claude/skills/${b.agent}/, execute its task for task ID ${taskId}, ` +
        `then call: npx convex run pipeline:completeBranch '{"taskId":"${taskId}","branchLabel":"${b.label}","agentName":"${b.agent}"}' --url http://localhost:3210`
    )
    .join("\n");

  const prompt = `You are a multi-agent dispatcher. Execute these agents sequentially for task ${taskId}:\n\n${agentInstructions}\n\nFor each agent, read its skill file, perform the work, and call completeBranch when done.`;

  const agentLog = resolve(LOG_DIR, `branch-${taskId.slice(-8)}-${model}.log`);
  const streamFile = resolve(STREAM_DIR, `${taskId}-${model}.jsonl`);
  const child = spawn(
    "claude",
    ["-p", prompt, "--model", model, "--dangerously-skip-permissions", "--output-format", "stream-json"],
    {
      cwd: PROJECT_DIR,
      stdio: ["ignore", "pipe", "pipe"],
      env: { ...process.env, HOME: process.env.HOME || "/root" },
      detached: true,
    }
  );

  child.stdout?.on("data", (data: Buffer) => {
    try { appendFileSync(streamFile, data); } catch {}
    try { appendFileSync(agentLog, data); } catch {}
  });
  child.stderr?.on("data", (data: Buffer) => {
    try { appendFileSync(agentLog, data); } catch {}
  });

  child.on("exit", (code) => {
    activeProcesses--;
    log(`BRANCH-DONE task=${taskId} branches=[${branchLabels}] exit=${code} (active=${activeProcesses})`);
    // Clean up stream file
    try { unlinkSync(streamFile); } catch {}
  });

  child.on("error", (err) => {
    activeProcesses--;
    log(`BRANCH-ERROR task=${taskId} err=${err.message}`);
    try { unlinkSync(streamFile); } catch {}
  });

  child.unref();
}

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (chunk: Buffer) => chunks.push(chunk));
    req.on("end", () => resolve(Buffer.concat(chunks).toString()));
    req.on("error", reject);
  });
}

function json(res: ServerResponse, data: unknown, status = 200) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url || "/", `http://127.0.0.1:${PORT}`);

  if (req.method === "GET" && url.pathname === "/health") {
    return json(res, { ok: true, active: activeProcesses });
  }

  if (req.method === "POST" && url.pathname === "/dispatch") {
    try {
      const body = JSON.parse(await readBody(req)) as { taskId: string; agentName: string };
      if (!body.taskId || !body.agentName) {
        return json(res, { error: "Missing taskId or agentName" }, 400);
      }
      spawnAgent(body.agentName, body.taskId);
      return json(res, { queued: true, agent: body.agentName, task: body.taskId });
    } catch (e: any) {
      log(`DISPATCH-ERROR: ${e.message}`);
      return json(res, { error: e.message }, 500);
    }
  }

  if (req.method === "POST" && url.pathname === "/dispatch-branch") {
    try {
      const body = JSON.parse(await readBody(req)) as {
        taskId: string;
        branches: { label: string; agent: string }[];
        model: string;
      };
      if (!body.taskId || !body.branches?.length || !body.model) {
        return json(res, { error: "Missing taskId, branches, or model" }, 400);
      }
      spawnBranchGroup(body.taskId, body.branches, body.model);
      return json(res, { queued: true, task: body.taskId, branchCount: body.branches.length });
    } catch (e: any) {
      log(`BRANCH-DISPATCH-ERROR: ${e.message}`);
      return json(res, { error: e.message }, 500);
    }
  }

  return json(res, { error: "Not found" }, 404);
});

server.listen(PORT, "0.0.0.0", () => {
  log(`Dispatcher listening on http://127.0.0.1:${PORT}`);
  log(`Project dir: ${PROJECT_DIR}`);
  log(`Invoke script: ${INVOKE_SCRIPT}`);
});
