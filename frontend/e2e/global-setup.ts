import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup for Playwright tests...');
  
  // Check if backend is running
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    // Try to reach the backend health endpoint
    try {
      const response = await page.request.get('http://localhost:8087/health');
      if (!response.ok()) {
        console.warn('⚠️ Backend health check failed. Some tests may fail.');
      } else {
        console.log('✅ Backend is running and healthy');
      }
    } catch (error) {
      console.warn('⚠️ Could not reach backend. Some tests may fail:', error);
    }
    
    await browser.close();
  } catch (error) {
    console.error('❌ Global setup failed:', error);
  }
  
  console.log('✅ Global setup completed');
}

export default globalSetup;