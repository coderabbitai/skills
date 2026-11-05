#!/usr/bin/env python3
"""Stream one selected Claude MCP result to the verified native CLI, in memory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
import uuid

MAX_TRANSCRIPT = 64 * 1024 * 1024
MAX_HANDOFF = 131072


class Invalid(Exception):
    pass


def regular_owned(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
        raise Invalid("Expected a regular file owned by the current user.")
    if info.st_mode & 0o022:
        raise Invalid("Refusing a file writable by another user.")
    return info


def verify_cli(path, checksum):
    regular_owned(path)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != checksum or not os.access(path, os.X_OK):
        raise Invalid("Native CLI checksum or executable permission mismatch.")


def decode_result(content):
    if isinstance(content, list):
        if len(content) != 1 or content[0].get("type") != "text":
            raise Invalid("Unsupported result content; do not copy the credential manually.")
        content = content[0].get("text")
    if not isinstance(content, str):
        raise Invalid("Unsupported result encoding.")
    return json.loads(content)


def read_handoff(transcript, session_id, review_id, workspace):
    if transcript.name != session_id + ".jsonl":
        raise Invalid("Transcript does not match the selected session.")
    if regular_owned(transcript).st_size > MAX_TRANSCRIPT:
        raise Invalid("Transcript exceeds the supported size.")
    calls, results = {}, {}
    with transcript.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.endswith("\n"):
                continue  # Native host may still be appending the final record.
            row = json.loads(line)
            if row.get("sessionId") != session_id:
                continue
            content = row.get("message", {}).get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if block.get("type") == "tool_use" and block.get("name") == "mcp__coderabbit__start_code_review":
                    key = block["id"]
                    value = block.get("input")
                    if key in calls and calls[key] != value:
                        raise Invalid("Conflicting replayed tool call.")
                    calls[key] = value
                elif block.get("type") == "tool_result":
                    key = block.get("tool_use_id")
                    # Keep only results for the selected connector's start calls.
                    if key not in calls:
                        continue
                    value = (block.get("is_error", False), block.get("content"))
                    if key in results and results[key] != value:
                        raise Invalid("Conflicting replayed tool result.")
                    results[key] = value
    matches = []
    for key, (is_error, content) in results.items():
        if is_error:
            continue
        response = decode_result(content)
        if not isinstance(response, dict) or response.get("review_id") != review_id:
            continue
        handoff = response.get("handoff")
        if not isinstance(handoff, dict) or handoff.get("review_id") != review_id:
            raise Invalid("Review response and handoff do not match.")
        options = calls[key]
        if not isinstance(options, dict):
            raise Invalid("Missing approved review options.")
        expected = {"scope": "all", **options}
        if handoff.get("options") != expected:
            raise Invalid("Handoff options differ from the approved tool call.")
        directory = expected.get("dir")
        if not directory or not Path(directory).is_absolute() or Path(directory).resolve() != workspace:
            raise Invalid("The tool call must name this exact absolute workspace.")
        if handoff.get("version") != 1 or handoff.get("launch_expires_at", 0) <= int(time.time() * 1000):
            raise Invalid("Handoff is unsupported or expired; inspect the original saved review.")
        payload = json.dumps(handoff, separators=(",", ":"))
        if len(payload.encode()) > MAX_HANDOFF:
            raise Invalid("Handoff exceeds the native CLI input limit.")
        matches.append(payload)
    if len(matches) != 1:
        raise Invalid("Expected exactly one matching start result; do not start another review.")
    return matches[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--dir", type=Path, required=True)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--session-id")
    parser.add_argument("--review-id")
    args = parser.parse_args()
    try:
        if not args.cli.is_absolute() or not args.dir.is_absolute():
            raise Invalid("CLI and workspace paths must be absolute.")
        workspace = args.dir.resolve(strict=True)
        verify_cli(args.cli, args.sha256)
        if args.preflight:
            return subprocess.run([str(args.cli), "--version"], check=False).returncode
        if not args.transcript or not args.session_id or not args.review_id:
            raise Invalid("Select a transcript, session ID and server-generated review ID.")
        uuid.UUID(args.session_id)
        uuid.UUID(args.review_id)
        payload = read_handoff(args.transcript, args.session_id, args.review_id, workspace)
        # No shell, credential arguments, environment variables, or new token files.
        result = subprocess.run(
            [str(args.cli), "review", "--agent", "--mcp-stdin", "--dir", str(workspace)],
            input=payload, text=True, cwd=workspace, check=False,
        )
        return result.returncode
    except Invalid as error:
        print("CodeRabbit bridge: " + str(error), file=sys.stderr)
    except (OSError, ValueError, TypeError, KeyError):
        # Never render parser exceptions containing tool result / credential text.
        print("CodeRabbit bridge: Unable to validate the selected local input.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
