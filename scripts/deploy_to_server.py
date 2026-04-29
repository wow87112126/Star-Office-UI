#!/usr/bin/env python3
"""Semi-automatic deploy helper for Star Office UI.

Flow:
1. Optional local smoke test
2. Create timestamped backup archive on server
3. Upload selected files/dirs from local workspace to remote project dir
4. Restart star-office service
5. Run remote health check
6. Optionally write a local deploy record template for Hermes/OpenClaw review

Designed to keep "code deploy" separate from "state bridge".
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import posixpath
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REMOTE_HOST = os.environ.get("STAR_OFFICE_SSH_HOST", "118.31.239.172")
DEFAULT_REMOTE_USER = os.environ.get("STAR_OFFICE_SSH_USER", "ecs-user")
DEFAULT_REMOTE_DIR = os.environ.get("STAR_OFFICE_REMOTE_DIR", "/home/ecs-user/Star-Office-UI")
DEFAULT_REMOTE_SERVICE = os.environ.get("STAR_OFFICE_REMOTE_SERVICE", "star-office")
DEFAULT_BASE_URL = os.environ.get("STAR_OFFICE_BASE_URL", "http://127.0.0.1:19000")
DEFAULT_HEALTH_URL = os.environ.get("STAR_OFFICE_HEALTH_URL", "http://127.0.0.1:19000/health")
DEFAULT_IDENTITY_FILE = os.environ.get("STAR_OFFICE_IDENTITY_FILE", "")
DEFAULT_RECORD_DIR = ROOT / "docs" / "deploy-records"

DEFAULT_INCLUDE = [
    "backend",
    "frontend",
    "office-agent-push.py",
    "set_state.py",
    "scripts/smoke_test.py",
    "healthcheck.sh",
]


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = True) -> int:
    print("[run]", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def capture(cmd: list[str], *, cwd: Path | None = None) -> str:
    return subprocess.check_output(cmd, cwd=str(cwd) if cwd else None, text=True).strip()


def ssh_target(user: str, host: str) -> str:
    return f"{user}@{host}"


def with_identity(cmd: list[str], identity_file: str) -> list[str]:
    if not identity_file:
        return cmd
    return cmd[:1] + ["-i", identity_file, "-o", "IdentitiesOnly=yes"] + cmd[1:]


def remote_path_join(base: str, rel: str) -> str:
    return posixpath.join(base.rstrip("/"), rel.replace("\\", "/"))


def default_record_file() -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return DEFAULT_RECORD_DIR / f"deploy-{stamp}.md"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=DEFAULT_REMOTE_HOST)
    ap.add_argument("--user", default=DEFAULT_REMOTE_USER)
    ap.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    ap.add_argument("--service", default=DEFAULT_REMOTE_SERVICE)
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--health-url", default=DEFAULT_HEALTH_URL)
    ap.add_argument("--identity-file", default=DEFAULT_IDENTITY_FILE)
    ap.add_argument("--skip-smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--scope", default="")
    ap.add_argument("--previous-commit", default="")
    ap.add_argument("--deploy-commit", default="")
    ap.add_argument("--record-file", default=str(default_record_file()))
    ap.add_argument(
        "--include",
        nargs="*",
        default=DEFAULT_INCLUDE,
        help="Relative paths under project root to upload",
    )
    return ap.parse_args()


def local_smoke(base_url: str) -> None:
    smoke = ROOT / "scripts" / "smoke_test.py"
    run([sys.executable, str(smoke), "--base-url", base_url], cwd=ROOT)


def resolve_deploy_commit(explicit: str) -> str:
    if explicit:
        return explicit
    return capture(["git", "rev-parse", "HEAD"], cwd=ROOT)


def remote_backup(target: str, remote_dir: str, identity_file: str, dry_run: bool) -> str:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = f"~/star-office-backup-{stamp}.tar.gz"
    cmd = with_identity([
        "ssh",
        target,
        f"tar -czf {backup} -C {posixpath.dirname(remote_dir)} {posixpath.basename(remote_dir)}",
    ], identity_file)
    if dry_run:
        print("[dry-run]", " ".join(cmd))
    else:
        run(cmd)
    return backup


def upload_paths(target: str, remote_dir: str, include: list[str], identity_file: str, dry_run: bool) -> None:
    for rel in include:
        src = ROOT / rel
        if not src.exists():
            print(f"[warn] skip missing: {rel}")
            continue
        dest = remote_path_join(remote_dir, rel)
        mkdir_cmd = with_identity(["ssh", target, f"mkdir -p {posixpath.dirname(dest)}"], identity_file)
        copy_cmd = with_identity(["scp", "-r", str(src), f"{target}:{dest}"], identity_file)
        if dry_run:
            print("[dry-run]", " ".join(mkdir_cmd))
            print("[dry-run]", " ".join(copy_cmd))
        else:
            run(mkdir_cmd)
            run(copy_cmd)


def remote_restart_and_check(target: str, service: str, health_url: str, identity_file: str, dry_run: bool) -> None:
    restart_cmd = with_identity(["ssh", target, f"sudo systemctl restart {service} && sudo systemctl status {service} --no-pager"], identity_file)
    health_cmd = with_identity(["ssh", target, f"curl -fsS {health_url}"], identity_file)
    if dry_run:
        print("[dry-run]", " ".join(restart_cmd))
        print("[dry-run]", " ".join(health_cmd))
    else:
        run(restart_cmd)
        run(health_cmd)


def write_deploy_record(record_file: Path, *, target: str, remote_dir: str, service: str, deploy_commit: str, previous_commit: str, scope: str, include: list[str], backup: str, dry_run: bool) -> None:
    record_file.parent.mkdir(parents=True, exist_ok=True)
    content = f"""# Deploy Record\n\n- timestamp: {dt.datetime.now().isoformat()}\n- operator: OpenClaw\n- reviewer: Hermes\n- environment: production\n- target: {target}\n- remote_dir: {remote_dir}\n- service: {service}\n- dry_run: {str(dry_run).lower()}\n- deploy_commit: {deploy_commit}\n- previous_known_good_commit: {previous_commit}\n- scope: {scope}\n- changed_paths:\n"""
    for item in include:
        content += f"  - {item}\n"
    content += f"""- backup_archive: {backup}\n- health_check: {'pending (dry-run)' if dry_run else 'completed by helper'}\n- rollback_target: {previous_commit}\n- notes: \n"""
    record_file.write_text(content, encoding="utf-8")
    print(f"[info] wrote deploy record: {record_file}")


def main() -> int:
    args = parse_args()
    target = ssh_target(args.user, args.host)
    deploy_commit = resolve_deploy_commit(args.deploy_commit)
    record_file = Path(args.record_file)

    print("== Star Office deploy helper ==")
    print(f"project root : {ROOT}")
    print(f"remote target: {target}:{args.remote_dir}")
    print(f"service      : {args.service}")
    print(f"deploy commit: {deploy_commit}")
    if args.previous_commit:
        print(f"previous good: {args.previous_commit}")
    if args.scope:
        print(f"scope        : {args.scope}")

    if not args.skip_smoke:
        local_smoke(args.base_url)

    backup = remote_backup(target, args.remote_dir, args.identity_file, args.dry_run)
    print(f"backup archive: {backup}")
    upload_paths(target, args.remote_dir, args.include, args.identity_file, args.dry_run)
    remote_restart_and_check(target, args.service, args.health_url, args.identity_file, args.dry_run)
    write_deploy_record(
        record_file,
        target=target,
        remote_dir=args.remote_dir,
        service=args.service,
        deploy_commit=deploy_commit,
        previous_commit=args.previous_commit,
        scope=args.scope,
        include=args.include,
        backup=backup,
        dry_run=args.dry_run,
    )
    print("[done] deploy flow completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
