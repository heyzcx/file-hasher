#!/usr/bin/env python3
"""file-hasher: compute and verify file checksums.

Usage:
    python3 file_hasher.py [-a ALGO] [--json] <path> [<path> ...]
    python3 file_hasher.py -c <checksum-file> [--json]

Examples:
    python3 file_hasher.py photo.jpg
    python3 file_hasher.py -a sha512 src/
    python3 file_hasher.py -c checksums.sha256
    find . -name '*.py' | xargs python3 file_hasher.py --json
"""
import argparse
import hashlib
import json
import os
import sys

ALGORITHMS = ("md5", "sha1", "sha256", "sha512", "blake2b")


def hash_file(path, algo):
    """Return the hex digest of one file, streaming in 1 MiB chunks."""
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_files(paths):
    """Expand paths into a sorted list of files (dirs walked recursively)."""
    files = []
    for p in paths:
        if os.path.isfile(p):
            files.append(p)
        elif os.path.isdir(p):
            for root, dirs, names in os.walk(p):
                dirs.sort()
                for name in sorted(names):
                    files.append(os.path.join(root, name))
        else:
            print(f"file-hasher: no such file or directory: {p}", file=sys.stderr)
    return files


def cmd_hash(paths, algo, as_json):
    files = collect_files(paths)
    if not files:
        return 2
    results = []
    for path in files:
        try:
            digest = hash_file(path, algo)
        except OSError as e:
            print(f"file-hasher: cannot read {path}: {e}", file=sys.stderr)
            return 2
        results.append({"file": path, "algo": algo, "hash": digest})
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['hash']}  {r['file']}")
    return 0


def cmd_check(checksum_file, as_json):
    """Verify files against a checksum file (sha256sum-style lines)."""
    try:
        with open(checksum_file, encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    except OSError as e:
        print(f"file-hasher: cannot read {checksum_file}: {e}", file=sys.stderr)
        return 2
    results = []
    failed = 0
    for line in lines:
        parts = line.split(None, 1)
        if len(parts) != 2:
            print(f"file-hasher: skipping bad line: {line}", file=sys.stderr)
            continue
        expected, path = parts
        path = path.lstrip("* ")
        algo = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}.get(len(expected))
        if algo is None:
            print(f"file-hasher: unknown hash length in line: {line}", file=sys.stderr)
            failed += 1
            continue
        try:
            actual = hash_file(path, algo)
        except OSError as e:
            print(f"file-hasher: cannot read {path}: {e}", file=sys.stderr)
            failed += 1
            continue
        ok = actual.lower() == expected.lower()
        if not ok:
            failed += 1
        results.append({"file": path, "algo": algo, "expected": expected,
                        "actual": actual, "ok": ok})
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            status = "OK" if r["ok"] else "FAILED"
            print(f"{r['file']}: {status}")
    if failed:
        print(f"file-hasher: {failed} file(s) failed verification", file=sys.stderr)
        return 1
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="file-hasher",
        description="Compute and verify file checksums (md5/sha1/sha256/sha512/blake2b).")
    parser.add_argument("paths", nargs="*", help="files or directories to hash")
    parser.add_argument("-a", "--algo", default="sha256", choices=ALGORITHMS,
                        help="hash algorithm (default: sha256)")
    parser.add_argument("-c", "--check", metavar="FILE",
                        help="verify files listed in a checksum file")
    parser.add_argument("--json", action="store_true", help="output results as JSON")
    args = parser.parse_args(argv)
    if args.check:
        return cmd_check(args.check, args.json)
    if not args.paths:
        parser.print_usage(sys.stderr)
        print("file-hasher: give files to hash, or -c <checksum-file> to verify",
              file=sys.stderr)
        return 2
    return cmd_hash(args.paths, args.algo, args.json)


if __name__ == "__main__":
    sys.exit(main())
