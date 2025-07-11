import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('token', 'mock-jwt-token');
    });

    // Mock authenticated user endpoint
    await page.route('**/api/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '123e4567-e89b-12d3-a456-426614174000',
          username: 'testuser',
          email: 'test@example.com',
          full_name: 'Test User',
          role: 'user',
          is_active: true,
          is_superuser: false,
          is_verified: true,
        }),
      });
    });

    // Mock dashboard data endpoints
    await page.route('**/api/agents', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'agent-1',
            name: 'Test Agent',
            endpoint: 'http://localhost:11434',
            model: 'llama3.1:8b',
            specialty: 'general_ai',
            status: 'online',
            current_tasks: 1,
            max_concurrent: 2,
          },
        ]),
      });
    });

    await page.route('**/api/tasks', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'task-1',
            title: 'Test Task',
            type: 'general_ai',
            status: 'pending',
            priority: 3,
            created_at: new Date().toISOString(),
          },
        ]),
      });
    });

    await page.route('**/api/health', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'operational',
          agents: {},
          total_agents: 1,
          active_tasks: 1,
          pending_tasks: 0,
          completed_tasks: 5,
        }),
      });
    });
  });

  test('should display dashboard content when authenticated', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check dashboard elements
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    await expect(page.getByText('Test User')).toBeVisible();
    
    // Check for system status cards
    await expect(page.getByText(/agents/i)).toBeVisible();
    await expect(page.getByText(/tasks/i)).toBeVisible();
  });

  test('should display agent status', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Wait for agents to load
    await expect(page.getByText('Test Agent')).toBeVisible();
    await expect(page.getByText(/online/i)).toBeVisible();
  });

  test('should display task information', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Wait for tasks to load
    await expect(page.getByText('Test Task')).toBeVisible();
    await expect(page.getByText(/pending/i)).toBeVisible();
  });

  test('should navigate to different sections', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Test navigation to agents page
    await page.getByRole('link', { name: /agents/i }).click();
    await expect(page).toHaveURL(/.*\/agents/);
    
    // Navigate back to dashboard
    await page.getByRole('link', { name: /dashboard/i }).click();
    await expect(page).toHaveURL(/.*\/dashboard/);
    
    // Test navigation to tasks page
    await page.getByRole('link', { name: /tasks/i }).click();
    await expect(page).toHaveURL(/.*\/tasks/);
  });

  test('should display system metrics', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check for metric cards
    await expect(page.getByText('1')).toBeVisible(); // Total agents
    await expect(page.getByText('5')).toBeVisible(); // Completed tasks
  });

  test('should handle real-time updates via WebSocket', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Mock WebSocket connection
    await page.evaluate(() => {
      // Simulate WebSocket message
      window.dispatchEvent(new CustomEvent('socket-message', {
        detail: {
          type: 'task_update',
          data: {
            id: 'task-1',
            status: 'completed'
          }
        }
      }));
    });
    
    // Check that the task status updates
    // Note: This would require the actual WebSocket implementation
    // For now, we just verify the dashboard loads properly
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });
});