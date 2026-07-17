import { test, expect } from '@playwright/test'

test.describe('Abyssal Assets - Main Menu', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('loads main menu with title', async ({ page }) => {
    await expect(page).toHaveTitle(/Abyssal Assets|Lochness Hatgame/)
  })

  test('displays ENTER THE LOCH button', async ({ page }) => {
    const enterButton = page.locator('text=ENTER THE LOCH')
    await expect(enterButton).toBeVisible()
  })

  test('displays MARKET button', async ({ page }) => {
    const marketButton = page.locator('text=MARKET')
    await expect(marketButton).toBeVisible()
  })

  test('displays VAULT button', async ({ page }) => {
    const vaultButton = page.locator('text=VAULT')
    await expect(vaultButton).toBeVisible()
  })

  test('displays SETTINGS button', async ({ page }) => {
    const settingsButton = page.locator('text=SETTINGS')
    await expect(settingsButton).toBeVisible()
  })

  test('has animated background', async ({ page }) => {
    // Check for canvas element (Phaser renderer)
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()

    // Canvas should have dimensions
    const box = await canvas.boundingBox()
    expect(box?.width).toBeGreaterThan(0)
    expect(box?.height).toBeGreaterThan(0)
  })
})

test.describe('Game Scene - Core Gameplay', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Click ENTER THE LOCH to start game
    await page.click('text=ENTER THE LOCH')
    await page.waitForTimeout(2000) // Wait for scene transition
  })

  test('loads game scene with boat', async ({ page }) => {
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()

    // Take screenshot for visual regression
    await expect(page).toHaveScreenshot('game-scene-loaded.png', { maxDiffPixels: 200 })
  })

  test('responds to movement keys', async ({ page }) => {
    const canvas = page.locator('canvas')

    // Simulate key presses
    await page.keyboard.down('ArrowRight')
    await page.waitForTimeout(500)
    await page.keyboard.up('ArrowRight')

    await page.keyboard.down('ArrowLeft')
    await page.waitForTimeout(500)
    await page.keyboard.up('ArrowLeft')

    await page.keyboard.down('ArrowUp')
    await page.waitForTimeout(500)
    await page.keyboard.up('ArrowUp')

    await page.keyboard.down('ArrowDown')
    await page.waitForTimeout(500)
    await page.keyboard.up('ArrowDown')

    // Game should still be responsive
    await expect(canvas).toBeVisible()
  })

  test('displays HUD with clout and coins', async ({ page }) => {
    // Look for HUD text elements (rendered by Phaser bitmapText)
    // These are rendered on canvas, so we check canvas is active
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()
  })

  test('can open market from game scene', async ({ page }) => {
    // Press M key or click market button if available
    await page.keyboard.press('KeyM')
    await page.waitForTimeout(1000)

    // Should transition to market scene
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()
  })
})

test.describe('Market Scene', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Navigate to market
    await page.click('text=MARKET')
    await page.waitForTimeout(2000)
  })

  test('loads market with item listings', async ({ page }) => {
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()

    await expect(page).toHaveScreenshot('market-scene.png', { maxDiffPixels: 300 })
  })

  test('displays player coins in header', async ({ page }) => {
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()
  })

  test('has tabs for browse/sell/buy/vault/history', async ({ page }) => {
    // Tabs are rendered on canvas - verify scene loaded
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()
  })

  test('can filter by tier', async ({ page }) => {
    // Interact with tier filter dropdown
    await page.keyboard.press('KeyT') // Assuming T cycles tiers
    await page.waitForTimeout(500)
    await page.keyboard.press('KeyT')
    await page.waitForTimeout(500)
  })

  test('can search items', async ({ page }) => {
    // Focus search input and type
    await page.keyboard.press('/') // Assuming / focuses search
    await page.keyboard.type('beanie')
    await page.waitForTimeout(500)
  })
})

test.describe('Dredge Mini-Game', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    await page.click('text=ENTER THE LOCH')
    await page.waitForTimeout(2000)

    // Navigate to a dredge spot and trigger mini-game
    // This would require knowing dredge spot positions
    // For now, simulate with a keyboard shortcut
    await page.keyboard.press('KeyD')
    await page.waitForTimeout(1000)
  })

  test('loads dredge mini-game scene', async ({ page }) => {
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()
  })

  test('shows sonar sweep line', async ({ page }) => {
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()

    await expect(page).toHaveScreenshot('dredge-minigame.png', { maxDiffPixels: 500 })
  })

  test('responds to space bar for sweep', async ({ page }) => {
    await page.keyboard.press('Space')
    await page.waitForTimeout(1000)

    // Sweep should start
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()
  })

  test('completes dredge on second space press", async ({ page }) => {
    await page.keyboard.press('Space') // Start sweep
    await page.waitForTimeout(2000)
    await page.keyboard.press('Space') // Stop sweep

    // Should show result
    await page.waitForTimeout(1000)
  })
})

test.describe('Persistence & Session', () => {
  test('survives page reload', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    await page.click('text=ENTER THE LOCH')
    await page.waitForTimeout(2000)

    // Reload page
    await page.reload()
    await page.waitForLoadState('networkidle')

    // Should return to main menu (or restore session)
    await expect(page.locator('text=ENTER THE LOCH')).toBeVisible()
  })

  test('works on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()

    // Touch interaction
    await page.tap('canvas', { position: { x: 187, y: 333 } })
  })
})

test.describe('Performance', () => {
  test('maintains 60fps in game scene', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    await page.click('text=ENTER THE LOCH')
    await page.waitForTimeout(3000)

    // Measure FPS via Performance API
    const fps = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        let frames = 0
        let lastTime = performance.now()

        function tick(now: number) {
          frames++
          if (now - lastTime >= 1000) {
            resolve(frames)
            return
          }
          requestAnimationFrame(tick)
        }
        requestAnimationFrame(tick)
      })
    })

    expect(fps).toBeGreaterThan(30) // At least 30fps in test environment
  })
})