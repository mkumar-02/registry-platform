import { execFileSync } from "child_process";
import fs from "fs";
import path from "path";

function pythonBin(): string {
  const apiVenv = path.resolve(__dirname, "../../.venv/bin/python");
  return fs.existsSync(apiVenv) ? apiVenv : "python3";
}

export function apiApproveIntake(submissionId: string): void {
  const script = path.join(__dirname, "../scripts/approve_fixture.py");
  execFileSync(pythonBin(), [script, "intake", submissionId], {
    env: process.env,
    encoding: "utf-8",
    stdio: ["ignore", "pipe", "inherit"],
  });
}

export function apiApproveChangeRequest(changeRequestId: string, sectionId?: string): void {
  const script = path.join(__dirname, "../scripts/approve_fixture.py");
  const args = [script, "cr", changeRequestId];
  if (sectionId) args.push(sectionId);
  execFileSync(pythonBin(), args, {
    env: process.env,
    encoding: "utf-8",
    stdio: ["ignore", "pipe", "inherit"],
  });
}
