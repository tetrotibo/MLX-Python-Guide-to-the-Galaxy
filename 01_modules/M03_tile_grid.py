# =============================================================================
# M03 - TILE GRID & WALLS: coordinates, inset tiles, wall bitmasks
# =============================================================================
#
# CONCEPTS:
#   - Tile coordinates vs pixel coordinates
#   - tile_px() / tile_py(): converting tile index to pixel position
#   - draw_tile(): filling interior of a tile (respecting wall inset)
#   - Drawing individual walls (north, south, east, west) as thin strips
#   - Wall bitmask encoding: how one integer describes all 4 walls
#   - Walls drawn after tiles: conventional with inset tiles, not required
#
#   Wall bitmask format:
#     bit 3 (0b1000) = West
#     bit 2 (0b0100) = South
#     bit 1 (0b0010) = East
#     bit 0 (0b0001) = North
#     Example: 0b1010 = West + East walls present
#
# WHAT WE ARE BUILDING:
#   A grid of colored tiles with inset walls between them - exact
#   visual structure used to render a maze. By end of this module
#   you will understand how any cell-based grid game is drawn with MLX.
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
)

TITLE = Path(__file__).stem

# =============================================================================
# CONFIG
# =============================================================================

TILE_SIZE = 80    # pixels per tile (interior + wall strips)
WALL_SIZE = 4     # wall strip thickness in pixels
BORDER = 1        # margin tiles around the grid
GRID_COLS = 11    # number of tile columns
GRID_ROWS = 8     # number of tile rows
W = (GRID_COLS + 2 * BORDER) * TILE_SIZE  # window width in pixels
H = (GRID_ROWS + 2 * BORDER) * TILE_SIZE  # window height in pixels

# =============================================================================
# INIT
# =============================================================================

m = mlx.Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, W, H, TITLE)
img_ptr = m.mlx_new_image(mlx_ptr, W, H)
img_addr, _, img_size_line, _ = m.mlx_get_data_addr(img_ptr)

# =============================================================================
# DRAWING PRIMITIVES
# =============================================================================

def write_pixel(x: int, y: int, color: int) -> None:
    """Write one pixel at (x, y) in BGR order. Skips out-of-bounds coords."""
    if not (0 <= x < W and 0 <= y < H):
        return

    byte_index = y * img_size_line + x * 4
    img_addr[byte_index] = color & 0xFF              # blue
    img_addr[byte_index + 1] = (color >> 8) & 0xFF   # green
    img_addr[byte_index + 2] = (color >> 16) & 0xFF  # red
    img_addr[byte_index + 3] = 0xFF                  # alpha

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
    """Convert tile column index to pixel x (top-left corner of tile).
    BORDER shifts grid inward so outermost wall strips never reach the
    window edge - write_rect uses raw slice assignment and raises
    ValueError if its range exceeds the buffer size.
    """
    return (tile_col + BORDER) * TILE_SIZE

def tile_py(tile_row: int) -> int:
    """Convert tile row index to pixel y (top-left corner of tile)."""
    return (tile_row + BORDER) * TILE_SIZE

# =============================================================================
# TILE DRAWING
# =============================================================================

def draw_tile(tile_col: int, tile_row: int, color: int) -> None:
    """Fill interior of a tile, leaving room for walls on all sides.
    A tile of TILE_SIZE pixels is NOT entirely filled with color.
    Outer WALL_SIZE pixels on each edge are reserved for wall strips.

    Visual layout (TILE_SIZE=8, WALL_SIZE=1):
        W W W W W W W W   <- north wall row
        W . . . . . . W   <- east/west wall columns
        W . . . . . . W
        W . . . . . . W   <- interior (. = filled here by draw_tile)
        W . . . . . . W
        W . . . . . . W
        W . . . . . . W
        W W W W W W W W   <- south wall row

    Without inset, two adjacent same-color tiles bleed into a solid block
    with no visible gap at open passages. Inset guarantees a WALL_SIZE strip
    of background at every edge, whether a wall is drawn there or not.
    """
    pixel_x = tile_px(tile_col) + WALL_SIZE
    pixel_y = tile_py(tile_row) + WALL_SIZE
    interior = TILE_SIZE - 2 * WALL_SIZE
    write_rect(pixel_x, pixel_y, interior, interior, color)

# =============================================================================
# WALL DRAWING
# =============================================================================

"""
APPROACH A - 4 walls per cell (this file):
    Each cell owns and draws all 4 of its wall strips independently.
    Each wall is trimmed at both corners by WALL_SIZE to avoid overlap -
    those corner pixels stay background color.

    Corner layout:
        . W W W W W .    <- north wall (trimmed at left and right corner)
        W . . . . . W    <- west wall (trimmed at top and bottom corner)
        W . . . . . W
        Corner (.) is never drawn - stays background color.

    Junction gap: every corner has a WALL_SIZE x WALL_SIZE hole.
    At WALL_SIZE = 1 it's a single pixel - invisible at normal distance.
    At WALL_SIZE = 4+ it becomes a visible notch and the approach breaks.

    Used in A-MAZE-ING. Choice was deliberate: each bit in the bitmask
    controls one of the cell's own walls - no neighbor logic needed.
    WALL_SIZE stayed at 1px throughout, keeping the gap invisible.

    Side effect: internal walls are 2 x WALL_SIZE thick (both neighbors
    draw their side). Edge walls are only 1 x WALL_SIZE - visually thinner.
    Fix: draw four extra strips/walls just outside the grid, one per side.

APPROACH B - west + north walls only (the cleaner option):
    Each cell draws only its west and north walls. South and east walls
    are handled by the neighbor cells below and to the right.
    Every wall pixel is owned by exactly one cell.

    Corner layout:
        W W W W W W W    <- north wall, full width, no trimming needed
        W . . . . . .    <- west wall, full height
        W . . . . . .
        Corners are always solid - no junction gap.

    WALL_SIZE can be as thick as needed. Corridor width equals
    TILE_SIZE - WALL_SIZE - one parameter controls both.

    Tradeoff: drawing a cell's south wall requires checking the neighbor
    below, not just the cell's own bitmask. More correct, more indirection.
    For thick, clean walls - use this.
"""

def draw_wall_north(tile_col: int, tile_row: int) -> None:
    """North wall: top edge strip, trimmed at both corners."""
    write_rect(tile_px(tile_col) + WALL_SIZE, tile_py(tile_row),
               TILE_SIZE - 2 * WALL_SIZE, WALL_SIZE, C_WALL)

def draw_wall_south(tile_col: int, tile_row: int) -> None:
    """South wall: bottom edge strip, trimmed at both corners."""
    write_rect(tile_px(tile_col) + WALL_SIZE,
               tile_py(tile_row) + TILE_SIZE - WALL_SIZE,
               TILE_SIZE - 2 * WALL_SIZE, WALL_SIZE, C_WALL)

def draw_wall_west(tile_col: int, tile_row: int) -> None:
    """West wall: left edge strip, trimmed at both corners."""
    write_rect(tile_px(tile_col), tile_py(tile_row) + WALL_SIZE,
               WALL_SIZE, TILE_SIZE - 2 * WALL_SIZE, C_WALL)

def draw_wall_east(tile_col: int, tile_row: int) -> None:
    """East wall: right edge strip, trimmed at both corners."""
    write_rect(tile_px(tile_col) + TILE_SIZE - WALL_SIZE,
               tile_py(tile_row) + WALL_SIZE,
               WALL_SIZE, TILE_SIZE - 2 * WALL_SIZE, C_WALL)

def draw_tile_walls(tile_col: int, tile_row: int, bitmask: int) -> None:
    """Draw walls encoded in a 4-bit bitmask.
    Bit layout:
      bit 3 (0b1000) = West
      bit 2 (0b0100) = South
      bit 1 (0b0010) = East
      bit 0 (0b0001) = North

    Extracting each bit: (bitmask >> bit_position) & 1
    If 1, that wall is present and gets drawn.
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
# SCENE
# =============================================================================

"""
LEFT  (cols 0-1): wall catalog - one tile per bitmask, open neighbors.
    Each tile is isolated so its walls read without interference.

    (col, row)  bitmask    walls present
    (0, 0)  0b0000   none
    (1, 0)  0b0001   north
    (0, 1)  0b0010   east
    (1, 1)  0b0100   south
    (0, 2)  0b1000   west
    (1, 2)  0b0011   north + east
    (0, 3)  0b0101   north + south  (vertical corridor)
    (1, 3)  0b1010   east  + west   (horizontal corridor)
    (0, 4)  0b0110   south + east   (corner)
    (1, 4)  0b1001   north + west   (corner)
    (0, 5)  0b1100   south + west   (corner)
    (1, 5)  0b0111   north + east + south
    (0, 6)  0b1011   north + east + west
    (1, 6)  0b1101   north + south + west
    (0, 7)  0b1110   east + south + west
    (1, 7)  0b1111   all walls (closed cell)

GAP   (col 2): background color - draw_tile is skipped for this column.

RIGHT (cols 3-10): 8x8 maze - two mirrored 4x4 spiral quadrants,
    connected at center. Entry top-left (col 3, row 0),
    exit bottom-right (col 10, row 7).
    Every shared edge is paired - all double-thickness bands are intentional.
"""

DEMO_GRID = [
    #  col0    col1  |  gap  |  col3    col4    col5    col6    col7    col8    col9    col10
    [0b0000, 0b0001,  0b0000,  0b1001, 0b0101, 0b0101, 0b0001, 0b0001, 0b0101, 0b0101, 0b0011],  # row 0
    [0b0010, 0b0100,  0b0000,  0b1010, 0b1001, 0b0011, 0b1010, 0b1010, 0b1001, 0b0011, 0b1010],  # row 1
    [0b1000, 0b0011,  0b0000,  0b1010, 0b1110, 0b1000, 0b0110, 0b1100, 0b0010, 0b1110, 0b1010],  # row 2
    [0b0101, 0b1010,  0b0000,  0b1100, 0b0101, 0b0010, 0b1001, 0b0011, 0b1000, 0b0101, 0b0110],  # row 3
    [0b0110, 0b1001,  0b0000,  0b1001, 0b0011, 0b1010, 0b1010, 0b1010, 0b1010, 0b1001, 0b0011],  # row 4
    [0b1100, 0b0111,  0b0000,  0b1010, 0b1010, 0b1100, 0b0010, 0b1000, 0b0110, 0b1010, 0b1010],  # row 5
    [0b1011, 0b1101,  0b0000,  0b1010, 0b1100, 0b0111, 0b1010, 0b1010, 0b1101, 0b0110, 0b1010],  # row 6
    [0b1110, 0b1111,  0b0000,  0b1100, 0b0101, 0b0101, 0b0100, 0b0100, 0b0101, 0b0101, 0b0110],  # row 7
]

write_rect(0, 0, W, H, C_BG)

for row in range(GRID_ROWS):
    for col in range(GRID_COLS):
        if col == 2:  # gap col - leave as C_FLOOR
            continue
        color = C_FLOOR
        if row == 0 and col == 3:
            color = C_ENTRY
        if row == GRID_ROWS - 1 and col == 10:
            color = C_EXIT
        draw_tile(col, row, color)

for row in range(GRID_ROWS):
    for col in range(GRID_COLS):
        draw_tile_walls(col, row, DEMO_GRID[row][col])

render()

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
#   - Change TILE_SIZE and WALL_SIZE and observe proportions
#   - Decrease WALL_SIZE from 4 to 1 and watch junction gap almost disappear
#   - Fix outer wall asymmetry: border edges are 1 x WALL_SIZE thick
#     while internal walls are 2 x WALL_SIZE. Draw four extra strips just
#     outside grid (using tile_px, tile_py, and WALL_SIZE) to make
#     all walls same visual weight.
# =============================================================================
