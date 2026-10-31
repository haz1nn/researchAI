#!/usr/bin/env python3
"""Recursive wrapper-peeler + flag grep.

Reads a file (or stdin with '-'), then BFS-decodes nested base64/base32/base85/
hex/rot-N/zlib/gzip/bz2/reverse layers and greps for the flag regex at every
layer. Prints any matches with the decode path that produced them.

Usage:
    python3 flaghunt.py <file|->  [--regex 'ctfcup\\{[^}]+\\}'] [--depth 6]
"""
import argparse
import base64
import binascii
import bz2
import gzip
import re
import sys
import zlib

DEFAULT_REGEX = r"ctfcup\{[^}]+\}"


def try_b64(b):
    s = re.sub(rb"\s", b"", b)
    if len(s) < 8 or len(s) % 4 != 0 or not re.fullmatch(rb"[A-Za-z0-9+/=]+", s):
        return None
    try:
        return base64.b64decode(s, validate=True)
    except Exception:
        return None


def try_b32(b):
    s = re.sub(rb"\s", b"", b).upper()
    if len(s) < 8 or len(s) % 8 != 0 or not re.fullmatch(rb"[A-Z2-7=]+", s):
        return None
    try:
        return base64.b32decode(s)
    except Exception:
        return None


def try_b85(b):
    s = re.sub(rb"\s", b"", b)
    if len(s) < 8:
        return None
    for fn in (base64.a85decode, base64.b85decode):
        try:
            out = fn(s)
            if out:
                return out
        except Exception:
            pass
    return None


def try_hex(b):
    s = re.sub(rb"\s", b"", b)
    if len(s) < 8 or len(s) % 2 != 0 or not re.fullmatch(rb"[0-9a-fA-F]+", s):
        return None
    try:
        return binascii.unhexlify(s)
    except Exception:
        return None


def try_zlib(b):
    try:
        return zlib.decompress(b)
    except Exception:
        try:
            return zlib.decompress(b, -15)
        except Exception:
            return None


def try_gzip(b):
    if not b.startswith(b"\x1f\x8b"):
        return None
    try:
        return gzip.decompress(b)
    except Exception:
        return None


def try_bz2(b):
    if not b.startswith(b"BZh"):
        return None
    try:
        return bz2.decompress(b)
    except Exception:
        return None


def try_reverse(b):
    return b[::-1]


def rotn_variants(b):
    try:
        t = b.decode("latin-1")
    except Exception:
        return []
    out = []
    for n in range(1, 26):
        rot = []
        for ch in t:
            if "a" <= ch <= "z":
                rot.append(chr((ord(ch) - 97 + n) % 26 + 97))
            elif "A" <= ch <= "Z":
                rot.append(chr((ord(ch) - 65 + n) % 26 + 65))
            else:
                rot.append(ch)
        out.append(("".join(rot)).encode("latin-1"))
    return out


DECODERS = [
    ("b64", try_b64),
    ("b32", try_b32),
    ("b85", try_b85),
    ("hex", try_hex),
    ("zlib", try_zlib),
    ("gzip", try_gzip),
    ("bz2", try_bz2),
    ("reverse", try_reverse),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--regex", default=DEFAULT_REGEX)
    ap.add_argument("--depth", type=int, default=6)
    args = ap.parse_args()

    data = sys.stdin.buffer.read() if args.target == "-" else open(args.target, "rb").read()
    rx = re.compile(args.regex.encode())

    seen = set()
    # queue of (bytes, path)
    queue = [(data, "raw")]
    found = set()

    while queue:
        cur, path = queue.pop(0)
        for m in rx.findall(cur):
            if m not in found:
                found.add(m)
                print(f"[FLAG] {m.decode('latin-1', 'replace')}   <= {path}")
        if path.count("/") >= args.depth:
            continue
        for name, fn in DECODERS:
            try:
                out = fn(cur)
            except Exception:
                out = None
            if not out or out == cur:
                continue
            h = hash(out[:4096])
            if h in seen:
                continue
            seen.add(h)
            queue.append((out, f"{path}/{name}"))
        # rot-N fan-out only near the top to limit explosion
        if path.count("/") <= 1:
            for i, rb in enumerate(rotn_variants(cur), 1):
                for m in rx.findall(rb):
                    if m not in found:
                        found.add(m)
                        print(f"[FLAG] {m.decode('latin-1','replace')}   <= {path}/rot{i}")

    if not found:
        print("[-] no flag match found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
