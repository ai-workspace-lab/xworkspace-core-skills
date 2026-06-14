---
name: Browser Automation
description: This skill should be used when the user needs to interact with web pages, browse websites, take screenshots, fill forms, click elements, extract web content, or perform any browser automation tasks. Trigger phrases include "open webpage", "visit website", "browse", "screenshot page", "fill form", "click button", "extract from website", "web scraping", "automate browser".
version: 1.0.0
---

# Browser Automation with agent-browser

Use `agent-browser` CLI tool for all browser automation tasks. This is the preferred method for web interactions.

## Important: Command Sequence

**Always follow this sequence:**

1. `agent-browser launch` - Start the browser first
2. `agent-browser open <url>` - Navigate to a URL
3. Perform operations (snapshot, click, type, etc.)
4. `agent-browser close` - Close when done

## Quick Reference

First, run `agent-browser` without arguments to see full help:

```bash
agent-browser
```

### Essential Commands

| Command | Description |
|---------|-------------|
| `agent-browser launch` | Start browser (required before open) |
| `agent-browser open <url>` | Navigate to URL |
| `agent-browser snapshot` | Get page content as text |
| `agent-browser snapshot -i` | Get page content with element IDs for interaction |
| `agent-browser screenshot` | Take screenshot |
| `agent-browser click <selector>` | Click an element |
| `agent-browser type <selector> <text>` | Type text into input |
| `agent-browser close` | Close browser |

### Common Workflows

**View webpage content:**
```bash
agent-browser launch
agent-browser open https://example.com
agent-browser snapshot
agent-browser close
```

**Take screenshot:**
```bash
agent-browser launch
agent-browser open https://example.com
agent-browser screenshot
agent-browser close
```

**Fill form and submit:**
```bash
agent-browser launch
agent-browser open https://example.com/login
agent-browser snapshot -i  # Get element IDs
agent-browser type "#username" "myuser"
agent-browser type "#password" "mypass"
agent-browser click "#submit"
agent-browser close
```

**Extract data from page:**
```bash
agent-browser launch
agent-browser open https://example.com/data
agent-browser snapshot  # Returns structured text content
agent-browser close
```

## Tips

1. **Always launch first**: `agent-browser open` will fail if browser isn't launched
2. **Use snapshot -i for interactions**: The `-i` flag shows element IDs needed for click/type
3. **Check help for more options**: Run `agent-browser <command> --help` for detailed options
4. **Close when done**: Always close the browser to free resources

## When NOT to Use

- For simple HTTP requests without JavaScript rendering, use `curl` or `WebFetch`
- For API calls, use appropriate HTTP tools
- agent-browser is for full browser automation with JavaScript support

## Troubleshooting

If `agent-browser` command not found:
```bash
npm install -g agent-browser
agent-browser install
```

If browser fails to launch on Linux:
```bash
agent-browser install --with-deps
```
