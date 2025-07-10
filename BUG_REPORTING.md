# 🐛 Hive Bug Reporting Process

This document outlines the process for reporting bugs discovered during Hive development.

## 🎯 Bug Reporting Criteria

Report bugs when you find:
- **Reproducible errors** in existing functionality
- **Performance regressions** compared to expected behavior
- **Security vulnerabilities** or authentication issues
- **Data corruption** or inconsistent state
- **API endpoint failures** returning incorrect responses
- **UI/UX issues** preventing normal operation
- **Docker/deployment issues** affecting system stability

## 📋 Bug Report Template

```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Hive Version: [commit hash]
- Component: [backend/frontend/mcp-server/docker]
- Browser: [if applicable]
- OS: Linux

## Error Logs
```
[error logs here]
```

## Additional Context
Any additional information that might be helpful
```

## 🔧 Bug Reporting Commands

### Create Bug Report
```bash
gh issue create \
  --title "Bug: [Short description]" \
  --body-file bug-report.md \
  --label "bug" \
  --assignee @me
```

### List Open Bugs
```bash
gh issue list --label "bug" --state open
```

### Update Bug Status
```bash
gh issue edit [issue-number] --add-label "in-progress"
gh issue close [issue-number] --comment "Fixed in commit [hash]"
```

## 🏷️ Bug Labels

- `bug` - Confirmed bug
- `critical` - System-breaking issue
- `security` - Security vulnerability
- `performance` - Performance issue
- `ui/ux` - Frontend/user interface bug
- `api` - Backend API issue
- `docker` - Container/deployment issue
- `mcp` - MCP server issue

## 📊 Bug Tracking

All bugs discovered during CCLI development will be tracked in GitHub Issues with:
- Clear reproduction steps
- Error logs and screenshots
- Component tags
- Priority labels
- Fix verification process

This ensures systematic tracking and resolution of all issues found during development.