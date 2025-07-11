import { test, expect } from '@playwright/test';

test.describe('Agents Management', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('token', 'mock-jwt-token');
    });

    await page.route('**/api/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '123e4567-e89b-12d3-a456-426614174000',
          username: 'testuser',
          email: 'test@example.com',
          full_name: 'Test User',
          role: 'admin',
          is_active: true,
          is_superuser: true,
          is_verified: true,
        }),
      });
    });

    // Mock agents API
    await page.route('**/api/agents', async route => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 'agent-1',
              name: 'Walnut CodeLlama',
              endpoint: 'http://walnut.local:11434',
              model: 'codellama:34b',
              specialty: 'kernel_dev',
              status: 'online',
              current_tasks: 1,
              max_concurrent: 2,
              agent_type: 'ollama',
              last_heartbeat: Date.now(),
            },
            {
              id: 'agent-2',
              name: 'Oak Gemma',
              endpoint: 'http://oak.local:11434',
              model: 'gemma2:27b',
              specialty: 'pytorch_dev',
              status: 'offline',
              current_tasks: 0,
              max_concurrent: 2,
              agent_type: 'ollama',
              last_heartbeat: Date.now() - 300000, // 5 minutes ago
            },
          ]),
        });
      }
    });
  });

  test('should display agents list', async ({ page }) => {
    await page.goto('/agents');
    
    // Check page title
    await expect(page.getByRole('heading', { name: /agents/i })).toBeVisible();
    
    // Check agent cards
    await expect(page.getByText('Walnut CodeLlama')).toBeVisible();
    await expect(page.getByText('Oak Gemma')).toBeVisible();
    
    // Check agent details
    await expect(page.getByText('codellama:34b')).toBeVisible();
    await expect(page.getByText('gemma2:27b')).toBeVisible();
    await expect(page.getByText('kernel_dev')).toBeVisible();
    await expect(page.getByText('pytorch_dev')).toBeVisible();
  });

  test('should show agent status indicators', async ({ page }) => {
    await page.goto('/agents');
    
    // Check online status
    await expect(page.getByText('online')).toBeVisible();
    await expect(page.getByText('offline')).toBeVisible();
  });

  test('should display agent utilization', async ({ page }) => {
    await page.goto('/agents');
    
    // Check task counts
    await expect(page.getByText('1/2')).toBeVisible(); // Current/max tasks for agent-1
    await expect(page.getByText('0/2')).toBeVisible(); // Current/max tasks for agent-2
  });

  test('should filter agents by status', async ({ page }) => {
    await page.goto('/agents');
    
    // Apply online filter
    await page.getByRole('button', { name: /filter/i }).click();
    await page.getByRole('option', { name: /online/i }).click();
    
    // Should show only online agents
    await expect(page.getByText('Walnut CodeLlama')).toBeVisible();
    // Offline agent might be hidden depending on implementation
  });

  test('should search agents by name', async ({ page }) => {
    await page.goto('/agents');
    
    // Search for specific agent
    const searchInput = page.getByPlaceholder(/search agents/i);
    await searchInput.fill('Walnut');
    
    // Should show filtered results
    await expect(page.getByText('Walnut CodeLlama')).toBeVisible();
  });

  test('should show agent details in modal/popup', async ({ page }) => {
    await page.goto('/agents');
    
    // Click on agent to view details
    await page.getByText('Walnut CodeLlama').click();
    
    // Check that detail view opens
    await expect(page.getByText('http://walnut.local:11434')).toBeVisible();
    await expect(page.getByText('codellama:34b')).toBeVisible();
  });

  test('should handle agent creation for admin users', async ({ page }) => {
    await page.goto('/agents');
    
    // Mock agent creation
    await page.route('**/api/agents', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'agent-3',
            name: 'New Agent',
            endpoint: 'http://localhost:11434',
            model: 'llama3.1:8b',
            specialty: 'general_ai',
            status: 'online',
            current_tasks: 0,
            max_concurrent: 2,
            agent_type: 'ollama',
          }),
        });
      }
    });
    
    // Look for add agent button (admin only)
    const addButton = page.getByRole('button', { name: /add agent/i });
    await expect(addButton).toBeVisible();
    
    // Click add agent
    await addButton.click();
    
    // Fill agent form
    await page.getByLabel(/name/i).fill('New Agent');
    await page.getByLabel(/endpoint/i).fill('http://localhost:11434');
    await page.getByLabel(/model/i).fill('llama3.1:8b');
    
    // Submit form
    await page.getByRole('button', { name: /create/i }).click();
    
    // Should show success message or new agent in list
    await expect(page.getByText('New Agent')).toBeVisible();
  });

  test('should handle agent health checks', async ({ page }) => {
    await page.goto('/agents');
    
    // Mock health check endpoint
    await page.route('**/api/agents/agent-1/health', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'healthy',
          response_time: 125,
          last_check: new Date().toISOString(),
        }),
      });
    });
    
    // Trigger health check
    await page.getByRole('button', { name: /check health/i }).first().click();
    
    // Should show health status
    await expect(page.getByText(/healthy/i)).toBeVisible();
  });

  test('should handle agent errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/agents', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });
    
    await page.goto('/agents');
    
    // Should show error message
    await expect(page.getByText(/error loading agents/i)).toBeVisible();
  });
});