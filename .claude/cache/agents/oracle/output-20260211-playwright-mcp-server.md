# Research Report: Playwright MCP Server for Claude Code

Generated: 2026-02-11

## Summary

The clear winner is **`@playwright/mcp`** -- the official Microsoft/Playwright team package. It has 25k+ GitHub stars, is actively maintained (latest release days ago), uses accessibility-tree-based interaction (fast and token-efficient), and is the de facto standard recommended by the community including Simon Willison. The community alternative `@executeautomation/playwright-mcp-server` has more features (device emulation, API testing) but is less maintained and more bloated.

## Candidates Evaluated

### 1. `@playwright/mcp` (RECOMMENDED)

| Attribute | Value |
|-----------|-------|
| **npm package** | `@playwright/mcp` |
| **GitHub repo** | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) |
| **GitHub stars** | ~25,200 |
| **Latest version** | 0.0.64 (published ~Feb 6, 2026) |
| **Maintainer** | Microsoft / Playwright team |
| **Architecture** | Accessibility-tree snapshots (not pixel-based) |
| **Confidence** | High |

**Why this one:**
- Official Microsoft package, same team that maintains Playwright itself
- Uses structured accessibility snapshots by default (fast, token-efficient, no vision model needed)
- Optional vision/screenshot mode via `--caps vision`
- Integrated into GitHub Copilot
- Most community adoption and documentation
- Simon Willison's recommended approach for Claude Code

### 2. `@executeautomation/playwright-mcp-server` (Alternative)

| Attribute | Value |
|-----------|-------|
| **npm package** | `@executeautomation/playwright-mcp-server` |
| **GitHub repo** | [executeautomation/mcp-playwright](https://github.com/executeautomation/mcp-playwright) |
| **Maintainer** | ExecuteAutomation (community) |
| **Architecture** | Screenshot-based + accessibility tree |
| **Confidence** | High |

**Pros:** 143 device emulations, API testing tools, test code generation
**Cons:** More tools = more token overhead, community-maintained, heavier

### 3. `@anthropics/mcp-playwright`

Does NOT exist. There is no Anthropic-published Playwright MCP package.

### 4. `claude-playwright` (npm)

A third-party wrapper. Not recommended -- use the official Microsoft package instead.

## Recommended .mcp.json Configuration

### Basic Configuration (Headless -- for servers/CI)

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless"
      ]
    }
  }
}
```

### With Vision/Screenshot Capability

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless",
        "--caps",
        "vision"
      ]
    }
  }
}
```

### Full Featured (Vision + PDF)

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless",
        "--caps",
        "vision,pdf"
      ]
    }
  }
}
```

### Desktop/Visible Browser (for interactive debugging)

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    }
  }
}
```

## CLI Installation Alternative

Instead of editing `.mcp.json` manually, you can use:

```bash
claude mcp add playwright -- npx @playwright/mcp@latest --headless
```

This persists to the project-level config for the current directory.

## Available Tools (Core -- Always Enabled)

| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to a URL |
| `browser_navigate_back` | Go back in history |
| `browser_navigate_forward` | Go forward in history |
| `browser_click` | Click an element (by accessibility ref or coordinates) |
| `browser_type` | Type text into a focused element |
| `browser_hover` | Hover over an element |
| `browser_drag` | Drag and drop |
| `browser_select_option` | Select from a dropdown |
| `browser_press_key` | Press a keyboard key |
| `browser_snapshot` | Capture accessibility tree snapshot (primary interaction mode) |
| `browser_take_screenshot` | Capture visual screenshot (PNG) |
| `browser_wait` | Wait for a condition |
| `browser_resize` | Resize the browser viewport |
| `browser_handle_dialog` | Accept/dismiss browser dialogs |
| `browser_evaluate` | Execute JavaScript in the page context |
| `browser_close` | Close the browser |
| `browser_choose_file` | Upload a file via file input |

### Tab Management Tools (Always Enabled)

| Tool | Description |
|------|-------------|
| `browser_tab_new` | Open a new tab |
| `browser_tab_select` | Switch to a specific tab |
| `browser_tab_close` | Close a tab |
| `browser_tab_list` | List all open tabs |

### Optional Capability Groups

| Capability | Enable With | Tools Added |
|------------|-------------|-------------|
| `vision` | `--caps vision` | Screenshot-based interaction mode (coordinate-based clicks) |
| `pdf` | `--caps pdf` | PDF generation from pages |
| `testing` | `--caps testing` | Test code generation |
| `tracing` | `--caps tracing` | Performance tracing |

## Operating Modes

### Snapshot Mode (Default)
- Reads the accessibility tree (structured text)
- Fast and lightweight
- Token-efficient (no base64 images in context)
- Elements referenced by accessibility labels/refs
- Best for most automation tasks

### Vision Mode (Opt-in via `--caps vision`)
- Captures screenshots
- Coordinate-based interactions (x, y clicks)
- Slower due to image processing
- Useful for canvas elements, graphical UIs, visual verification
- Requires a vision-capable model

## Key Flags

| Flag | Description |
|------|-------------|
| `--headless` | Run browser without visible window |
| `--browser chromium\|firefox\|webkit` | Choose browser engine (default: chromium) |
| `--caps <list>` | Enable additional capabilities (comma-separated) |
| `--isolated` | Use isolated browser context (no shared state) |
| `--storage-state <path>` | Load saved auth/cookies from file |
| `--no-sandbox` | Disable Chromium sandbox (needed in some containers) |

## Usage Tips for Claude Code

1. **First invocation:** Explicitly say "Use the playwright MCP to navigate to..." -- otherwise Claude may try to use Bash with Playwright CLI instead.
2. **Headless on servers:** Always use `--headless` on Linux servers without a display.
3. **Token efficiency:** The default snapshot mode is much more token-efficient than vision mode. Only enable vision when you need visual verification.
4. **Auth persistence:** Use `--storage-state` to save and reuse login sessions.

## Sources

1. [microsoft/playwright-mcp GitHub](https://github.com/microsoft/playwright-mcp) - Official repository, 25k+ stars
2. [@playwright/mcp on npm](https://www.npmjs.com/package/@playwright/mcp) - npm package page
3. [Simon Willison: Using Playwright MCP with Claude Code](https://til.simonwillison.net/claude-code/playwright-mcp-claude-code) - Practical setup guide
4. [executeautomation/mcp-playwright GitHub](https://github.com/executeautomation/mcp-playwright) - Community alternative
5. [@executeautomation/playwright-mcp-server on npm](https://www.npmjs.com/package/@executeautomation/playwright-mcp-server) - Community npm package
6. [Playwright MCP on LobeHub](https://lobehub.com/mcp/microsoft-playwright-mcp-main) - Community listing with tool details
7. [Autify: Playwright MCP Server Guide](https://autify.com/blog/playwright-mcp) - Detailed capability breakdown
