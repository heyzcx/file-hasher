# file-hasher

Compute and verify file checksums — a zero-dependency Python CLI.

## Features

- Hash one file, several files, or whole directories (walked recursively)
- Algorithms: md5, sha1, sha256 (default), sha512, blake2b
- Verify files against a `sha256sum`-style checksum file, auto-detecting the
  algorithm from the hash length
- Plain or `--json` output, for piping into other tools
- Streams files in 1 MiB chunks, so large files use almost no memory

## Requirements

Python 3.8+ — no third-party packages.

## Usage

```bash
# Hash a single file (sha256 by default)
python3 file_hasher.py photo.jpg

# Hash several files with md5
python3 file_hasher.py -a md5 a.txt b.txt

# Hash a whole directory recursively
python3 file_hasher.py -a sha512 src/

# Machine-readable output
python3 file_hasher.py --json *.zip

# Create a checksum file, then verify it later
python3 file_hasher.py backup.tar.gz > checksums.sha256
python3 file_hasher.py -c checksums.sha256
```

Output format matches `sha256sum`: `<hash>  <file>`.

Verify mode prints `<file>: OK` or `<file>: FAILED` for each entry and exits
with status 1 if any file fails (2 for usage / read errors, 0 when all pass).

## Example

```bash
$ python3 file_hasher.py example.txt
a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447  example.txt

$ python3 file_hasher.py -c checksums.sha256
example.txt: OK
```

## License

MIT
