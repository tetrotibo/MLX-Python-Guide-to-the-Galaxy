# =============================================================================
# M04 - DRAW ORDER & LAYERS: compositor pattern, flat pixel buffer, UI split
# =============================================================================
#
# CONCEPTS:
#   - There are NO real layers in MLX - just one flat pixel buffer
#   - "Layering" = draw order: last draw wins
#   - The compositor pattern: one named function per conceptual layer
#   - Separating maze area from UI panel (two x-regions)
#
#   Draw stack (bottom to top):
#     Maze area -------------------------------------------
#     1. floor fill          - background + all tile interiors
#     2. pattern tiles       - special cells drawn over floor
#     3. path                - solution path drawn over pattern
#     4. entry / exit tiles  - drawn AFTER path, always visible
#     5. walls               - drawn after tiles (conventional)
#     UI panel --------------------------------------------
#     6. UI background       - fills the right panel
#     7. UI content          - drawn over panel background
#
# WHAT WE ARE BUILDING:
#   A static multi-element scene (background, grid, path, overlay, UI panel)
#   drawn once in correct order using the compositor pattern.
#
# CONTROLS:
#   ESC:    quit
#
# =============================================================================

import mlx  # type: ignore
from pathlib import Path
from config import (  # type: ignore
    EVENT_KEY_PRESS, EVENT_WINDOW_CLOSE,
    MASK_KEY_PRESS, MASK_NONE,
    KEY_ESC,
    C_BG, C_FLOOR, C_WALL, C_ENTRY, C_EXIT,
    C_PATH, C_PATTERN, C_UI_BG, C_UI_ACTIVE, C_UI_INACTIVE,
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

TILE_SIZE = 80    # pixels per tile (interior + wall strips)
WALL_SIZE = 1     # wall strip thickness in pixels
GRID_COLS = 8     # number of tile columns
GRID_ROWS = 8     # number of tile rows
BORDER = 1        # margin tiles around the grid
UI_W = 400        # width of the UI panel in pixels
UI_BTN_H = 30          # button height in pixels
UI_BTN_W = UI_W - 120  # button width (60px padding on each side)
MAZE_W = (GRID_COLS + 2 * BORDER) * TILE_SIZE  # maze area width in pixels
WIN_H = (GRID_ROWS + 2 * BORDER) * TILE_SIZE   # window height in pixels
WIN_W = MAZE_W + UI_W                          # window width in pixels

# =============================================================================
# INIT
# =============================================================================

m = mlx.Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, WIN_W, WIN_H, TITLE)
img_ptr = m.mlx_new_image(mlx_ptr, WIN_W, WIN_H)
img_addr, _, img_size_line, _ = m.mlx_get_data_addr(img_ptr)

# =============================================================================
# DRAWING PRIMITIVES
# =============================================================================

def write_rect(x: int, y: int, w: int, h: int, color: int) -> None:
    """Fill a rectangle using fast row slice assignment."""
    blue = color & 0xFF
    green = (color >> 8) & 0xFF
    red = (color >> 16) & 0xFF
    row = bytearray([blue, green, red, 0xFF] * w)
    for row_offset in range(h):
        start = (y + row_offset) * img_size_line + x * 4
        end = start + len(row)
        img_addr[start:end] = row

def render() -> None:
    """Push image buffer to window."""
    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

# =============================================================================
# TILE COORDINATES
# =============================================================================

def tile_px(tile_col: int) -> int:
    """Convert tile column index to pixel x (top-left corner of tile)."""
    return (tile_col + BORDER) * TILE_SIZE

def tile_py(tile_row: int) -> int:
    """Convert tile row index to pixel y (top-left corner of tile)."""
    return (tile_row + BORDER) * TILE_SIZE

# =============================================================================
# TILE DRAWING
# =============================================================================

def draw_tile(tile_col: int, tile_row: int, color: int) -> None:
    """Fill interior of a tile, inset by WALL_SIZE on all sides."""
    inset = WALL_SIZE
    interior_size = TILE_SIZE - 2 * inset
    write_rect(tile_px(tile_col) + inset, tile_py(tile_row) + inset,
               interior_size, interior_size, color)

# =============================================================================
# WALL DRAWING
# =============================================================================

def draw_wall_north(tile_col: int, tile_row: int) -> None:
    write_rect(tile_px(tile_col) + WALL_SIZE, tile_py(tile_row),
               TILE_SIZE - 2 * WALL_SIZE, WALL_SIZE, C_WALL)

def draw_wall_south(tile_col: int, tile_row: int) -> None:
    write_rect(tile_px(tile_col) + WALL_SIZE,
               tile_py(tile_row) + TILE_SIZE - WALL_SIZE,
               TILE_SIZE - 2 * WALL_SIZE, WALL_SIZE, C_WALL)

def draw_wall_west(tile_col: int, tile_row: int) -> None:
    write_rect(tile_px(tile_col), tile_py(tile_row) + WALL_SIZE,
               WALL_SIZE, TILE_SIZE - 2 * WALL_SIZE, C_WALL)

def draw_wall_east(tile_col: int, tile_row: int) -> None:
    write_rect(tile_px(tile_col) + TILE_SIZE - WALL_SIZE,
               tile_py(tile_row) + WALL_SIZE,
               WALL_SIZE, TILE_SIZE - 2 * WALL_SIZE, C_WALL)

def draw_tile_walls(tile_col: int, tile_row: int, bitmask: int) -> None:
    """Draw walls encoded in a 4-bit bitmask (from M03).
    bit 3 = West, bit 2 = South, bit 1 = East, bit 0 = North
    """
    if (bitmask >> 3) & 1:
        draw_wall_west(tile_col, tile_row)
    if (bitmask >> 2) & 1:
        draw_wall_south(tile_col, tile_row)
    if (bitmask >> 1) & 1:
        draw_wall_east(tile_col, tile_row)
    if (bitmask >> 0) & 1:
        draw_wall_north(tile_col, tile_row)

# =============================================================================
# SCENE DATA
# =============================================================================

# Taken from M03 (right section, cols 3-10 remapped to 0-7).
# Entry top-left (0, 0), exit bottom-right (7, 7).
# Two mirrored 4x4 spiral quadrants connected at the center.
MAZE_GRID = [
    #  col0    col1    col2    col3    col4    col5    col6    col7
    [0b1001, 0b0101, 0b0101, 0b0001, 0b0001, 0b0101, 0b0101, 0b0011],  # row 0
    [0b1010, 0b1001, 0b0011, 0b1010, 0b1010, 0b1001, 0b0011, 0b1010],  # row 1
    [0b1010, 0b1110, 0b1000, 0b0110, 0b1100, 0b0010, 0b1110, 0b1010],  # row 2
    [0b1100, 0b0101, 0b0010, 0b1111, 0b1111, 0b1000, 0b0101, 0b0110],  # row 3
    [0b1001, 0b0011, 0b1010, 0b1111, 0b1111, 0b1010, 0b1001, 0b0011],  # row 4
    [0b1010, 0b1010, 0b1100, 0b0011, 0b1001, 0b0110, 0b1010, 0b1010],  # row 5
    [0b1010, 0b1100, 0b0111, 0b1010, 0b1010, 0b1101, 0b0110, 0b1010],  # row 6
    [0b1100, 0b0101, 0b0101, 0b0100, 0b0100, 0b0101, 0b0101, 0b0110],  # row 7
]

ENTRY = (0, 0)
EXIT = (7, 7)

# Solution path through maze (col, row)
PATH = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (2, 4), (2, 5),
        (3, 5), (3, 6), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7)]

# Pattern tiles - none overlap PATH
PATTERN = [(3, 3), (4, 3), (3, 4), (4, 4)]

# =============================================================================
# COMPOSITOR LAYERS
# =============================================================================

def draw_floor() -> None:
    """Layer 1: Fill window background, then all maze tile interiors.
    Background covers the full window including the border margin.
    Everything else draws on top of this.
    """
    write_rect(0, 0, WIN_W, WIN_H, C_BG)
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            draw_tile(col, row, C_FLOOR)

def draw_pattern() -> None:
    """Layer 2: Pattern tiles - decorative cells, drawn over floor."""
    for tile_col, tile_row in PATTERN:
        draw_tile(tile_col, tile_row, C_PATTERN)

def draw_path() -> None:
    """Layer 3: Solution path, drawn after pattern tiles."""
    for tile_col, tile_row in PATH:
        draw_tile(tile_col, tile_row, C_PATH)

def draw_overlay() -> None:
    """Layer 4 + 5: Entry, exit, and all walls.
    Entry and exit are drawn AFTER path so they are always visible
    even if the path passes through them.
    Walls are drawn after tile fills - with inset tiles this is
    conventional, not required: wall strips and tile interiors occupy
    different pixels and never overlap.
    """
    draw_tile(*ENTRY, C_ENTRY)
    draw_tile(*EXIT,  C_EXIT)
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            draw_tile_walls(col, row, MAZE_GRID[row][col])

def draw_ui() -> None:
    """Layer 6 + 7: UI panel - a completely separate x-region.
    UI panel lives to the right of the maze (x >= MAZE_W).
    Never overlaps maze area - drawn independently.
    """
    ui_center_x = MAZE_W + UI_W // 2
    write_rect(MAZE_W, 0, UI_W, WIN_H, C_UI_BG)
    labels = [
        (UI_BTN_W, UI_BTN_H, C_UI_ACTIVE),
        (UI_BTN_W, UI_BTN_H, C_UI_INACTIVE),
        (UI_BTN_W, UI_BTN_H, C_UI_INACTIVE),
        (UI_BTN_W, UI_BTN_H, C_UI_INACTIVE),
    ]
    for i, (label_w, label_h, label_color) in enumerate(labels):
        label_x = ui_center_x - label_w // 2
        label_y = TILE_SIZE + i * (UI_BTN_H * 2)
        write_rect(label_x, label_y, label_w, label_h, label_color)

# =============================================================================
# SCENE RENDER
# =============================================================================

def render_scene() -> None:
    """Draw entire scene in correct layer order, then push.
    Each line is one conceptual layer. Order is everything:
    a later call draws over an earlier one wherever they overlap.
    """
    draw_floor()
    draw_pattern()
    draw_path()
    draw_overlay()
    draw_ui()
    render()

render_scene()

# =============================================================================
# HOOKS
# =============================================================================

def key_press_handler(keycode: int, param) -> int:
    if keycode == KEY_ESC:
        m.mlx_loop_exit(mlx_ptr)
    return 0

def close_handler(param) -> int:
    m.mlx_loop_exit(mlx_ptr)
    return 0

m.mlx_hook(win_ptr, EVENT_KEY_PRESS, MASK_KEY_PRESS, key_press_handler, None)
m.mlx_hook(win_ptr, EVENT_WINDOW_CLOSE, MASK_NONE, close_handler, None)

# =============================================================================
# LOOP
# =============================================================================

m.mlx_loop(mlx_ptr)

# =============================================================================
# CLEANUP
# =============================================================================

m.mlx_destroy_image(mlx_ptr, img_ptr)
m.mlx_destroy_window(mlx_ptr, win_ptr)
m.mlx_release(mlx_ptr)

# =============================================================================
# WHAT TO TRY NEXT:
#   - Move draw_overlay() before draw_path()
#     -> draw_path() overwrites entry and exit with C_PATH
#   - Move draw_floor() after draw_path()
#     -> draw_floor() overwrites all tile interiors with C_FLOOR
#   - Move draw_ui() before draw_floor()
#     -> draw_floor() overwrites UI panel with C_FLOOR
# =============================================================================
