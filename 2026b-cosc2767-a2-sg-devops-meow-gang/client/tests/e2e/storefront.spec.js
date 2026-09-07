// RMIT University Vietnam
// Course: COSC2767 Systems Deployment and Operations
// Semester: 2026B
// Assessment: Assignment 2
// Author: Ngo Hoang Long
// ID: s4142456
// Created date: 03/09/2026
// Last modified: 03/09/2026
// Acknowledgement: Playwright documentation.

import { test, expect } from '@playwright/test'

// Test anonymous storefront browsing and product navigation.
test('anonymous user can browse the storefront', async ({ page }) => {
  await page.goto('/shop')

  await expect(page.getByRole('heading', { name: 'All merchandise' })).toBeVisible()

  const product = page.locator('.product-card').first()
  await expect(product).toBeVisible()
  await expect(product.locator('img')).toBeVisible()

  await product.locator('a.product-card__name').click()
  await expect(page).toHaveURL(/\/product\//)
  await expect(page.getByRole('button', { name: 'Add to bag' })).toBeVisible()
})

// Test the high-value customer journey, including declined then approved payment.
test('customer can recover from declined payment and place an order', async ({ page }) => {
  const email = `playwright-${Date.now()}@example.com`
  const password = 'Playwright123!'

  await page.goto('/register')
  await page.locator('#first-name').fill('Playwright')
  await page.locator('#last-name').fill('Customer')
  await page.locator('#email').fill(email)
  await page.locator('#password').fill(password)
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/dashboard/)

  await page.goto('/shop')
  const product = page.locator('.product-card').first()
  await expect(product).toBeVisible()
  await product.locator('a.product-card__name').click()
  await page.getByRole('button', { name: 'Add to bag' }).click()

  // ProductView opens the bag automatically after adding the item.
  await expect(page.getByRole('dialog', { name: 'Your bag' })).toBeVisible()

  await page.locator('#card-number').fill('4000 0000 0000 0002')
  await page.locator('#card-expiry').fill('12/30')
  await page.locator('#card-cvc').fill('123')
  await page.locator('#card-name').fill('Playwright Customer')
  await page.getByRole('button', { name: 'Pay and place order' }).click()
  await expect(page.getByText('Your card was declined.')).toBeVisible()

  await page.locator('#card-number').fill('4242 4242 4242 4242')
  await page.getByRole('button', { name: 'Pay and place order' }).click()
  await expect(page).toHaveURL(/\/order\/success\/\d+$/)
  await expect(page.getByText(/Thank you|order/i).first()).toBeVisible()
})
