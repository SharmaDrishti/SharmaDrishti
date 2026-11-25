"""Compact the approved SVG panels for use as GitHub README images."""

import argparse
import re
from decimal import Decimal
from pathlib import Path


ASSETS = Path(__file__).resolve().parents[1] / "assets"
SOURCE = ASSETS / "maritime"
DESTINATION = ASSETS / "profile"
PANELS = ("intro", "mnemoai", "repolens", "technical", "technical-mobile", "beyond")

# Glyph outlines from scripts.typo use only these commands and fixed-point coordinates.
GLYPH_PATH = re.compile(r'<path d="(M[-0-9., MLCQZ]+)"(?= fill="#[0-9a-fA-F]{6}"/>)')
SEGMENT = re.compile(r"([MLCQZ])([^MLCQZ]*)")
COORDINATE = re.compile(r"-?\d+\.\d{2}")


def number(value):
    if value == 0:
        return "0"
    compact = format(value, "f")
    if "." in compact:
        compact = compact.rstrip("0").rstrip(".")
    if compact.startswith("0."):
        return compact[1:]
    if compact.startswith("-0."):
        return "-" + compact[2:]
    return compact


def encode(command, coordinates):
    values = [number(value) for value in coordinates]
    return command + "".join(
        ("," if index and value[0] != "-" else "") + value
        for index, value in enumerate(values)
    )


def compact_glyph(path):
    current = start = (Decimal(0), Decimal(0))
    segments = []
    for command, data in SEGMENT.findall(path):
        if command == "Z":
            segments.append(command)
            current = start
            continue

        values = [Decimal(raw) for raw in COORDINATE.findall(data)]
        if len(values) != {"M": 2, "L": 2, "Q": 4, "C": 6}[command]:
            return path
        absolute = encode(command, values)
        relative = encode(
            command.lower(), [value - current[index % 2] for index, value in enumerate(values)]
        )
        segments.append(min((absolute, relative), key=len))
        current = tuple(values[-2:])
        if command == "M":
            start = current
    return "".join(segments)


def package(svg):
    return GLYPH_PATH.sub(lambda match: f'<path d="{compact_glyph(match[1])}"', svg)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    check = parser.parse_args().check
    if not check:
        DESTINATION.mkdir(exist_ok=True)

    before = after = 0
    for name in PANELS:
        file = f"{name}.svg"
        original = (SOURCE / file).read_text(encoding="utf-8")
        output = package(original).encode("utf-8")
        target = DESTINATION / file
        if check:
            if target.read_bytes() != output:
                raise SystemExit(f"{target} needs to be repackaged")
        else:
            target.write_bytes(output)
        before += len(original.encode("utf-8"))
        after += len(output)
    print(f"Six profile SVGs: {before:,} → {after:,} bytes ({1 - after / before:.1%} smaller).")


if __name__ == "__main__":
    main()
