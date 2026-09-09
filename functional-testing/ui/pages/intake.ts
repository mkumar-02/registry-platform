import { Page, expect } from "@playwright/test";
import { localePath, loadFixture } from "../helpers/fixture";
import { searchInTopBar } from "../helpers/auth";

export async function openIntakeList(page: Page) {
  const fx = loadFixture();
  await page.goto(localePath(fx.locale, `/intake-form/${fx.register_mnemonic}`), {
    waitUntil: "domcontentloaded",
  });
  await expect(page).toHaveURL(new RegExp(`/intake-form/${fx.register_mnemonic}`, "i"));
}

export async function searchIntakeAndOpen(page: Page, firstName: string, submissionId: string) {
  const fx = loadFixture();
  await openIntakeList(page);
  await searchInTopBar(page, firstName);

  const link = page.locator(`a[href*="${submissionId}"]`).first();
  if (await link.isVisible({ timeout: 20_000 }).catch(() => false)) {
    await link.click();
  } else {
    await page.goto(
      localePath(fx.locale, `/intake-form/${fx.register_mnemonic}/submission/${submissionId}`),
      { waitUntil: "domcontentloaded" }
    );
  }

  await expect(page).toHaveURL(new RegExp(submissionId));
  const body = page.locator("body");
  await expect(body).toContainText(new RegExp(`${firstName}|${submissionId.slice(0, 8)}`, "i"));
}
