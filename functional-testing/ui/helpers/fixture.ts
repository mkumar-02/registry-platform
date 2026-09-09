import fs from "fs";
import path from "path";

export type ProvisionedFixture = {
  register_mnemonic: string;
  locale: string;
  individual: {
    internal_record_id: string;
    first_name: string;
    middle_name: string;
    last_name: string;
    submission_id: string;
  };
  pending_intake: {
    submission_id: string;
    first_name: string;
    middle_name: string;
    last_name: string;
  };
  pending_cr: {
    change_request_id: string;
    first_name: string;
    new_middle_name: string;
    section_id: string;
  };
};

export function loadFixture(): ProvisionedFixture {
  const fixturePath = path.join(__dirname, "..", "fixtures", "provisioned.json");
  if (!fs.existsSync(fixturePath)) {
    throw new Error(`Missing ${fixturePath} — run global setup / npm run provision`);
  }
  return JSON.parse(fs.readFileSync(fixturePath, "utf-8"));
}

export function localePath(locale: string, suffix: string): string {
  const clean = suffix.startsWith("/") ? suffix : `/${suffix}`;
  return `/${locale}${clean}`;
}
