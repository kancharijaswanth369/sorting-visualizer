import pygame
import random
import sys

pygame.init()

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1000, 600
WINDOW        = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Algorithm Visualizer – v2")

FONT  = pygame.font.SysFont("arial", 18)
FPS   = 120               # Change for faster / slower animation
BARS  = 120               # Number of bars to sort
PADDING_SIDE = 60
PADDING_TOP  = 130
BAR_MIN = 10
BAR_MAX = HEIGHT - PADDING_TOP

# ─────────────────────────────────────────────────────────────
# Color palette (material‑inspired)
# ─────────────────────────────────────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (  0,   0,   0)
GREY    = (189, 189, 189)
RED     = (239,  83,  80)   # Comparing / swapping
BLUE    = ( 66, 165, 245)   # Left sub‑array (merge sort)
ORANGE  = (255, 167,  38)   # Right sub‑array (merge sort)
YELLOW  = (255, 238,  88)   # Write pointer
GREEN   = ( 76, 175,  80)   # Finished / sorted

# ─────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────

def make_dataset(n: int):
    """Random list of ints inside drawing bounds."""
    return [random.randint(BAR_MIN, BAR_MAX) for _ in range(n)]


def draw_controls():
    """Render key‑bindings & colour legend."""
    notes = [
        "R – Reset",              "SPACE – Play / Pause", "",
        "B – Bubble sort",        "I – Insertion sort",   "S – Selection sort",
        "M – Merge sort (fixed)", "Q – Quick sort",       "",
        "Colour key:",
        "Red   – Comparing / swapping",
        "Blue  – Left half (merge)",
        "Orange– Right half (merge)",
        "Yellow– Write pointer",
        "Green – Sorted"
    ]
    y = 10
    for line in notes:
        label = FONT.render(line, True, BLACK)
        WINDOW.blit(label, (10, y))
        y += label.get_height() + 4


def draw_bars(data, colours=None):
    """Draw all bars with optional per‑index colour mapping."""
    if colours is None:
        colours = {}
    WINDOW.fill(WHITE)
    draw_controls()

    bar_width = max(1, (WIDTH - 2 * PADDING_SIDE) // len(data))
    for i, val in enumerate(data):
        x = PADDING_SIDE + i * bar_width
        y = HEIGHT - val
        colour = colours.get(i, GREY)
        pygame.draw.rect(WINDOW, colour, (x, y, bar_width, val))
    pygame.display.update()

# ─────────────────────────────────────────────────────────────
# Sorting algorithm generators
# Every yield returns (continue_flag, colour_mapping)
# ─────────────────────────────────────────────────────────────

def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - i - 1):
            yield True, {j: RED, j + 1: RED}
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                yield True, {j: RED, j + 1: RED}
    yield True, {idx: GREEN for idx in range(n)}
    yield False, {}


def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            yield True, {j: RED, j + 1: YELLOW}
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    yield True, {idx: GREEN for idx in range(len(arr))}
    yield False, {}


def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield True, {j: RED, min_idx: RED}
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        yield True, {i: YELLOW, min_idx: YELLOW}
    yield True, {idx: GREEN for idx in range(n)}
    yield False, {}


def merge_sort(arr):
    """Recursive generator‑based merge sort with vivid colour cues."""

    def _merge_sort(left, right):
        if left >= right:
            return
        mid = (left + right) // 2
        yield from _merge_sort(left, mid)
        yield from _merge_sort(mid + 1, right)
        yield from merge(left, mid, right)

    def merge(left, mid, right):
        left_part  = arr[left:mid + 1]
        right_part = arr[mid + 1:right + 1]
        i = j = 0
        k = left
        while i < len(left_part) and j < len(right_part):
            highlight = {left + i: BLUE, mid + 1 + j: ORANGE, k: YELLOW}
            yield True, highlight
            if left_part[i] <= right_part[j]:
                arr[k] = left_part[i]
                i += 1
            else:
                arr[k] = right_part[j]
                j += 1
            k += 1
            yield True, highlight
        while i < len(left_part):
            highlight = {left + i: BLUE, k: YELLOW}
            yield True, highlight
            arr[k] = left_part[i]
            i += 1
            k += 1
            yield True, highlight
        while j < len(right_part):
            highlight = {mid + 1 + j: ORANGE, k: YELLOW}
            yield True, highlight
            arr[k] = right_part[j]
            j += 1
            k += 1
            yield True, highlight

    yield from _merge_sort(0, len(arr) - 1)
    yield True, {idx: GREEN for idx in range(len(arr))}
    yield False, {}


def quick_sort(arr):
    stack = [(0, len(arr) - 1)]
    while stack:
        low, high = stack.pop()
        if low >= high:
            continue
        pivot = arr[high]
        i = low
        for j in range(low, high):
            yield True, {j: RED, high: YELLOW}
            if arr[j] < pivot:
                arr[i], arr[j] = arr[j], arr[i]
                yield True, {i: RED, j: RED}
                i += 1
        arr[i], arr[high] = arr[high], arr[i]
        yield True, {i: GREEN}
        stack.append((low, i - 1))
        stack.append((i + 1, high))
    yield True, {idx: GREEN for idx in range(len(arr))}
    yield False, {}

# ─────────────────────────────────────────────────────────────
# Main application loop
# ─────────────────────────────────────────────────────────────

def main():
    data = make_dataset(BARS)
    running  = False
    sorter   = None
    clock    = pygame.time.Clock()

    while True:
        clock.tick(FPS)

        # Step the active sorter
        if running and sorter is not None:
            try:
                cont, colours = next(sorter)
                draw_bars(data, colours)
                if not cont:
                    running = False
            except StopIteration:
                running = False
        else:
            draw_bars(data)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:                 # Reset list
                    data = make_dataset(BARS)
                    running = False
                if running:                                 # Ignore new algo keys mid‑run
                    continue
                if event.key == pygame.K_SPACE and sorter:  # Pause / resume
                    running = not running
                elif event.key == pygame.K_b:
                    sorter = bubble_sort(data)
                    running = True
                elif event.key == pygame.K_i:
                    sorter = insertion_sort(data)
                    running = True
                elif event.key == pygame.K_s:
                    sorter = selection_sort(data)
                    running = True
                elif event.key == pygame.K_m:
                    sorter = merge_sort(data)
                    running = True
                elif event.key == pygame.K_q:
                    sorter = quick_sort(data)
                    running = True


if __name__ == "__main__":
    main()
