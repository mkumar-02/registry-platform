import { Page, expect } from "@playwright/test";
import { localePath, loadFixture } from "../helpers/fixture";
import { searchInTopBar } from "../helpers/auth";

export async function openRegister(page: Page) {
  const fx = loadFixture();
  const path = localePath(fx.locale, `/register/${fx.register_mnemonic}`);
  await page.goto(path, { waitUntil: "domcontentloaded" });
  await expect(page).toHaveURL(new RegExp(`/register/${fx.register_mnemonic}`, "i"));
}

export async function searchAndOpenRecord(page: Page, firstName: string, internalRecordId: string) {
  const fx = loadFixture();
  await openRegister(page);
  await searchInTopBar(page, firstName);

  const link = page.locator(`a[href*="/register/${fx.register_mnemonic}/${internalRecordId}"]`).first();
  if (await link.isVisible({ timeout: 20_000 }).catch(() => false)) {
    await link.click();
  } else {
    await page.goto(
      localePath(fx.locale, `/register/${fx.register_mnemonic}/${internalRecordId}`),
      { waitUntil: "domcontentloaded" }
    );
  }

  await expect(page).toHaveURL(new RegExp(internalRecordId));
  await expect(page.getByText(firstName, { exact: false }).first()).toBeVisible({ timeout: 30_000 });
}
