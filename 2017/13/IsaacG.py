import collections
import itertools
import math

PARAMETERIZED_INPUTS = [True, False]
INPUT_PARSER = aoc.parse_ints_per_line

def solver(parsed_input: list[list[int]], part_one: bool) -> int:
    ranges: dict[int, int] = dict(sorted(parsed_input))  # type: ignore
    intervals = {depth: (range_ - 1) * 2 for depth, range_ in ranges.items()}

    # Part one: sum(range * depth) for each sensor that would catch us (i.e. position == 0).
    if part_one:
        return sum(
            ranges[depth] * depth
            for depth, interval in intervals.items()
            if depth % interval == 0
        )

    # Part two: return the smallest delay for which we can avoid being caught.
    # Brute force: 4.7s
    # Sieve: 3.4s
    # Groupwise progressive solver: 2ms
    return part_two_groupwise(intervals)

def part_two_groupwise(intervals: dict[int, int]) -> int:
    """Progressive group-wise solver - 2ms.

    We are trying to solve for a delay which allows us to make it past all the scanners.
    Scanners are periodic with some `interval`.
    The combined period of all the scanners is `lcm(intervals)`.
    If the solution is 123 then `123 + period * k` would get us pass the scanners for all values of `k`.
    There may be multiple ways to get through all the scanners, eg `123 + period * k` and `456 + period * k`.
    I will denote those as `{123, 456} + period * k`.

    The problem can be broken down into groups.
    For the approach, a group is a collection of scanners with the same period.
    For any subset of scanners, there is a set of solutions which will pass through those scanners.
    Solutions can be (1) computed for each group and then (2) combined.

    1. Computing solutions for a group.

    Note: a scanner with period 4 and depth 1 is functionally equivalent to a scanner with period 4 and depth (1 + 4 * k).
    When computing the depths for a scanner, we can use `depth % interval` to simplify.

    If we have a group of scanners which all have a period of 4, we can denote all soltutions as a subset of `{0, 1, 2, 3} + 4 * k`.
    The depth of the scanners tells us which starts are not valid.
    If a scanner has period 4, the scanner will be at location 0 after `4 * k`.
    We will arrive at the scanner after `delay + depth` ticks.
    We require that `delay + depth != 4 * k` or `delay != 4 * k - depth`.
    Considering only the first interval (k = 1) that gives invalid start delays of `4 - depth` or `period - depth`.
    Valid starts are what remains: `set(range(period)) - invalid_starts`.

    2. Combining group solutions.

    Combining solutions requires finding where the solutions overlap -- values that valid for both groups.
    The combined solution will always be a subset of the solutions which hold for both groups;
    the combined solution will be valid for both groups but may be more specific/narrow.

    If two groups have solutions `{1, 2, 3} + 5 * k` and `{2, 3, 4} + 5 * k` then the combined solution is {2, 3} + 5 * k`.
    Those start delays would get us pass the scanners for both groups.

    When the period for the groups differ, we need to "normalize" the solutions to use a common period (the lcm).
    If two groups have solutions `{1} + 2 * k` and `{2} + 3 * k`, we can rewrite those in terms of the lcm 6:
    `{1, 3, 5} + 6 * k` and {2, 5} + 6 * k`. Once the period matches, the combined solution is `{5} + 6 * k`.

    Note: actually expanding can be expensive when the two periods are very different.
    Instead I expand the solution with the larger period (fewer values generates) then check if those would be in the other solution.

    This combination can be applied repeatedly until all groups are accounted for, then the min(delays) is the answer.
    """
    # Group scanners by period/interval.
    groups = collections.defaultdict(set)
    for depth, interval in intervals.items():
        groups[interval].add(depth % interval)

    # Solve the valid solutions for each group.
    group_solutions = {}
    for interval, depths in groups.items():
        invalid_delays = {(interval - depth) % interval for depth in depths}
        group_delays = set(range(interval)) - invalid_delays
        group_solutions[interval] = group_delays

    # Initial solution: any delay is valid, i.e. 0 + 1 * k
    combined_period, combined_delays = 1, {0}

    # Start with the groups with the fewest solutions to keep the solution space size down.
    for group_interval, group_delays in sorted(group_solutions.items(), key=lambda i: len(i[1])):
        # Find the LCM to expand the delays.
        new_step = math.lcm(group_interval, combined_period)
        # Generator which yields all the expanded delays.
        expanded_delays = (
            delay + i
            for i in range(0, new_step, combined_period)
            for delay in combined_delays
        )
        # Filter out delays which are not valid for this group of scanners.
        combined_delays = {delay for delay in expanded_delays if delay % group_interval in group_delays}
        combined_period = new_step
    # Return the smallest valid delay.
    return min(combined_delays)

def part_two_sieve(intervals: dict[int, int]) -> int:
    """Sieve - 3.4s.

    Use a Sieve of Eratosthenes.
    For each scanner, eliminate invalid delays.
    When we are done, the smallest valid value is the answer.

    Note: A sieve requires knowing the upper limit.
    Not knowing the limit, I simply try powers of 10 until it fits.
    """
    # Note, convert intervals to a list for faster iteration.
    intervals_list = list(intervals.items())
    intervals_list.sort(reverse=False, key=lambda a: a[1])

    for i in range(2, 10):
        size = 10 ** i

        delays = [True] * size
        for depth, interval in intervals_list:
            for delay in range(interval - depth, size, interval):
                delays[delay] = False
        if found := next((i for i in range(size) if delays[i]), None):
            return found
    raise RuntimeError("Not found.")

def part_two_brute_force(intervals: dict[int, int]) -> int:
    """Brute force - 4.7s.

    Try all delays until one can pass all scanners.
    """
    # Note, convert intervals to a list for faster iteration.
    intervals_list = list(intervals.items())
    intervals_list.sort(reverse=False, key=lambda a: a[1])

    return next(
        delay
        for delay in itertools.count()
        if all((delay + depth) % interval for depth, interval in intervals_list)
    )
