#!/bin/python
"""Advent of Code, Day 21: Fractal Art."""

SHIFT = complex(1, 1)
SUBPIXELS = {i: {complex(x, y) for x in range(i) for y in range(i)} for i in [2, 3]}
InputType = dict[int, dict[frozenset[complex], set[complex]]]
PARAMETERIZED_INPUTS = [5, 18]

def to_complex_set(pattern: str) -> set[complex]:
    """Convert a hash pattern to a set of complex numbers indicating which location is on."""
    return {
        complex(x, y)
        for y, part in enumerate(pattern.split("/"))
        for x, char in enumerate(part)
        if char == "#"
    }

START = to_complex_set(".#./..#/###")

def permutations(pixels: frozenset[complex], block_size: int) -> list[frozenset[complex]]:
    """Return all permutations of a block of pixels (flipped and rotated, 8 values)."""
    hashes = set(pixels)

    # Shift the pattern to center around (0, 0) to make flip/rotate simpler.
    if block_size == 2:
        hashes = {i * 2 for i in hashes}
    hashes = {i - SHIFT for i in hashes}
    flipped = {complex(-i.real, +i.imag) for i in hashes}
    # Rotate and flip.
    matches = [
        {i * 1j ** rot for i in j} for rot in range(4)
        for j in [hashes, flipped]
    ]
    # Unshift.
    matches = [
        {i + SHIFT for i in hashes}
        for hashes in matches
    ]
    if block_size == 2:
        matches = [{i / 2 for i in hashes} for hashes in matches]
    return [frozenset(i) for i in matches]

def solver(parsed_input: InputType, param: int) -> int:
    """Return the number of pixels which are on after repeating the image enhancement."""
    pixels = START
    replacements = parsed_input
    size = 3

    for _ in range(2 if testing else param):
        blocksize_in = 3 if size % 2 else 2
        blockcount = size // blocksize_in
        blocksize_out = blocksize_in + 1

        size += blockcount

        # For each sub-block, shift the block to (0,0), enhance and unshift.
        new_pixels = set()
        for y in range(blockcount):
            for x in range(blockcount):
                corner_in = complex(x * blocksize_in, y * blocksize_in)
                subpixels_in = frozenset({
                    p for p in SUBPIXELS[blocksize_in] if corner_in + p in pixels
                })
                corner_out = complex(x * blocksize_out, y * blocksize_out)
                subpixels_out = {
                    corner_out + p for p in replacements[blocksize_in][subpixels_in]
                }
                new_pixels.update(subpixels_out)

        pixels = new_pixels

    return len(pixels)

def input_parser(puzzle_input: str) -> InputType:
    """Parse the input data."""
    rules: InputType = {2: {}, 3: {}}
    for line in puzzle_input.splitlines():
        match, _, replace = line.split()
        block_size = match.count("/") + 1
        rules[block_size][frozenset(to_complex_set(match))] = to_complex_set(replace)

    # Build the enhance dict.
    return {
        block_size: {
            match: replace
            for match, replace in block_rules.items()
            for match in permutations(match, block_size)
        }
        for block_size, block_rules in rules.items()
    }
