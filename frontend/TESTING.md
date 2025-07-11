# Frontend Testing Infrastructure

This document describes the testing setup for the Hive frontend application.

## Overview

The testing infrastructure includes:
- **Unit Tests**: Jest + React Testing Library for component and hook testing
- **End-to-End Tests**: Playwright for full user journey testing
- **Type Checking**: TypeScript compiler for type safety
- **Linting**: ESLint for code quality

## Test Commands

### Unit Tests
```bash
# Run all unit tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage report
npm run test:coverage
```

### End-to-End Tests
```bash
# Run e2e tests headlessly
npm run test:e2e

# Run e2e tests with UI
npm run test:e2e:ui

# Debug e2e tests
npm run test:e2e:debug
```

### All Tests
```bash
# Run both unit and e2e tests
npm run test:all
```

## Test Structure

### Unit Tests
- Location: `src/**/__tests__/` or `src/**/*.test.tsx`
- Framework: Jest + React Testing Library
- Configuration: `jest.config.js`
- Setup: `src/test/setup.ts`
- Utilities: `src/test/utils.tsx`

Example test file structure:
```
src/
├── components/
│   └── auth/
│       ├── LoginForm.tsx
│       └── __tests__/
│           └── LoginForm.test.tsx
├── hooks/
│   └── __tests__/
│       └── useSocketIO.test.ts
└── test/
    ├── setup.ts
    └── utils.tsx
```

### End-to-End Tests
- Location: `e2e/`
- Framework: Playwright
- Configuration: `playwright.config.ts`
- Global Setup: `e2e/global-setup.ts`

Example e2e test structure:
```
e2e/
├── auth.spec.ts
├── dashboard.spec.ts
├── agents.spec.ts
└── global-setup.ts
```

## Testing Best Practices

### Unit Testing
1. **Test user interactions, not implementation details**
2. **Use semantic queries** (getByRole, getByLabelText)
3. **Mock external dependencies** (APIs, WebSocket)
4. **Test error states and loading states**
5. **Maintain high coverage** (70%+ threshold)

### E2E Testing
1. **Test critical user journeys**
2. **Mock API responses** for consistent testing
3. **Use Page Object Model** for complex interactions
4. **Test responsive design** across viewports
5. **Include accessibility checks**

### Mocking Strategies

#### API Mocking (Unit Tests)
```typescript
jest.mock('../../api/auth');
const mockAuthApi = authApi as jest.Mocked<typeof authApi>;

mockAuthApi.login.mockResolvedValue(mockApiResponses.auth.login);
```

#### API Mocking (E2E Tests)
```typescript
await page.route('**/api/auth/login', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify(mockResponse),
  });
});
```

## Coverage Requirements

- **Statements**: 70%
- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%

## CI/CD Integration

Tests run automatically on:
- Push to main branches
- Pull requests
- Frontend code changes

GitHub Actions workflow: `.github/workflows/frontend-tests.yml`

## Debugging Tests

### Unit Tests
```bash
# Debug specific test
npm run test -- --testNamePattern="LoginForm"

# Debug with Node.js inspector
node --inspect-brk node_modules/.bin/jest --runInBand
```

### E2E Tests
```bash
# Run in headed mode
npm run test:e2e:debug

# Run specific test
npx playwright test auth.spec.ts

# Open test results
npx playwright show-report
```

## Test Data

Mock data is centralized in `src/test/utils.tsx`:
- `mockUser`: Test user data
- `mockAgent`: Test agent data
- `mockTask`: Test task data
- `mockApiResponses`: API response templates

## Environment Setup

### Prerequisites
- Node.js 18+
- Chrome/Chromium (for Playwright)

### Installation
```bash
cd frontend
npm install
npx playwright install chromium
```

### Configuration Files
- `jest.config.js`: Jest configuration
- `playwright.config.ts`: Playwright configuration
- `src/test/setup.ts`: Jest test setup
- `e2e/global-setup.ts`: Playwright global setup

## Common Issues

### Jest Issues
- **Module resolution**: Check `moduleNameMapping` in jest.config.js
- **Async tests**: Use `act()` for async operations
- **React warnings**: Mock console methods in setup

### Playwright Issues
- **Timeouts**: Increase timeout in playwright.config.ts
- **Flaky tests**: Add proper wait conditions
- **Browser not found**: Run `npx playwright install`

## Contributing

When adding new features:
1. Write unit tests for components/hooks
2. Add e2e tests for new user flows
3. Update mock data if needed
4. Ensure coverage thresholds are met
5. Test both success and error scenarios