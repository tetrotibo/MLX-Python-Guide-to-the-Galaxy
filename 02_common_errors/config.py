# =============================================================================
# config.py - MLX Keycode Reference
# =============================================================================

# Set OS to match your environment ("MAC" or "LINUX"), if you need to use
# different keys than the ones used in this guide.

OS = "LINUX"

# =============================================================================
# DO NOT EDIT BELOW THIS LINE
# =============================================================================

def _key(linux_code, mac_code):
    return linux_code if OS == "LINUX" else mac_code


# EVENTS --------------------------------------------------
# X11 event type IDs - same on Linux and Mac.

EVENT_KEY_PRESS = 2
EVENT_KEY_RELEASE = 3
EVENT_WINDOW_CLOSE = 33  # X button

# EVENT MASKS ---------------------------------------------
# Second argument to mlx_hook - filters which sub-events fire the callback.
MASK_KEY_PRESS   = 1  # KeyPress:   fire on any key
MASK_KEY_RELEASE = 2  # KeyRelease: fire on any key
MASK_NONE        = 0  # all other events (window close, etc.)

# CONTROL -------------------------------------------------
KEY_ESC   = _key(65307, 65307)          # same on both
KEY_SPACE = _key(32,    32)             # same on both

# ARROWS --------------------------------------------------
KEY_LEFT  = _key(65361, 65361)          # same on both
KEY_RIGHT = _key(65363, 65363)          # same on both
KEY_UP    = _key(65362, 65362)          # same on both
KEY_DOWN  = _key(65364, 65364)          # same on both

# FUNCTION KEYS -------------------------------------------
KEY_F1 = _key(65470, 65470)             # same on both
KEY_F2 = _key(65471, 65471)             # same on both
KEY_F3 = _key(65472, 65472)             # same on both
KEY_F4 = _key(65473, 65473)             # same on both

# TOP ROW (number keys) -----------------------------------
KEY_0 = _key(48, 48)                    # same on both
KEY_1 = _key(49, 49)                    # same on both
KEY_2 = _key(50, 50)                    # same on both
KEY_3 = _key(51, 51)                    # same on both
KEY_4 = _key(52, 52)                    # same on both
KEY_5 = _key(53, 53)                    # same on both
KEY_6 = _key(54, 54)                    # same on both
KEY_7 = _key(55, 55)                    # same on both
KEY_8 = _key(56, 56)                    # same on both
KEY_9 = _key(57, 57)                    # same on both

# -- ALPHABET ---------------------------------------------
KEY_A = _key(97,  97)                   # same on both
KEY_B = _key(98,  98)                   # same on both
KEY_C = _key(99,  99)                   # same on both
KEY_D = _key(100, 100)                  # same on both
KEY_E = _key(101, 101)                  # same on both
KEY_F = _key(102, 102)                  # same on both
KEY_G = _key(103, 103)                  # same on both
KEY_H = _key(104, 104)                  # same on both
KEY_I = _key(105, 105)                  # same on both
KEY_J = _key(106, 106)                  # same on both
KEY_K = _key(107, 107)                  # same on both
KEY_L = _key(108, 108)                  # same on both
KEY_M = _key(109, 109)                  # same on both
KEY_N = _key(110, 110)                  # same on both
KEY_O = _key(111, 111)                  # same on both
KEY_P = _key(112, 112)                  # same on both
KEY_Q = _key(113, 113)                  # same on both
KEY_R = _key(114, 114)                  # same on both
KEY_S = _key(115, 115)                  # same on both
KEY_T = _key(116, 116)                  # same on both
KEY_U = _key(117, 117)                  # same on both
KEY_V = _key(118, 118)                  # same on both
KEY_W = _key(119, 119)                  # same on both
KEY_X = _key(120, 120)                  # same on both
KEY_Y = _key(121, 121)                  # same on both
KEY_Z = _key(122, 122)                  # same on both

# NUMPAD --------------------------------------------------
# All confirmed on Mac via XQuartz. Linux codes assume Num Lock OFF.
KEY_NUMPAD_0     = _key(65438, 65456)
KEY_NUMPAD_1     = _key(65436, 65457)
KEY_NUMPAD_2     = _key(65433, 65458)
KEY_NUMPAD_3     = _key(65435, 65459)
KEY_NUMPAD_4     = _key(65430, 65460)
KEY_NUMPAD_5     = _key(65437, 65461)
KEY_NUMPAD_6     = _key(65432, 65462)
KEY_NUMPAD_7     = _key(65429, 65463)
KEY_NUMPAD_8     = _key(65431, 65464)
KEY_NUMPAD_9     = _key(65434, 65465)
KEY_NUMPAD_PLUS  = _key(65451, 65451)  # same on both
KEY_NUMPAD_MINUS = _key(65453, 65453)  # same on both
KEY_NUMPAD_STAR  = _key(65450, 65450)  # same on both
KEY_NUMPAD_SLASH = _key(65455, 65455)  # same on both
KEY_NUMPAD_DOT   = _key(65439, 65454)
KEY_NUMPAD_ENTER = _key(65421, 65421)  # same on both


# =============================================================================
# COLORS
# =============================================================================
# Shared palette used across all modules. Import what you need.
# All values are 0xRRGGBB - written to the buffer in BGR order by write_rect.

# utility colors - pure hues, softened to match guide palette mood
C_WHITE   = 0xDDDDDD      # soft white
C_RED     = 0xBB3333      # soft red
C_GREEN   = 0x33BB33      # soft green
C_BLUE    = 0x3333BB      # soft blue
C_CYAN    = 0x33BBBB      # soft cyan
C_MAGENTA = 0xBB33BB      # soft magenta
C_YELLOW  = 0xBBBB33      # soft yellow

# project colors
C_BG          = 0x323232  # charcoal
C_FLOOR       = 0x404040  # dark grey
C_WALL        = 0xDDDDDD  # silver
C_ENTRY       = 0x2A4C73  # steel blue
C_EXIT        = 0x2A4C73  # steel blue
C_PATH        = 0x499847  # moss green
C_PATTERN     = 0xF9A013  # amber
C_PLAYER      = 0xA54900  # burnt orange
C_UI_BG       = 0x1D1D1D  # jet black
C_UI_ACTIVE   = 0xA54900  # burnt orange
C_UI_INACTIVE = 0x2A4C73  # steel blue

# =============================================================================
# TEXT
# =============================================================================
# Fixed character dimensions for the built-in MLX bitmap font.
# Used by put_text_centered() in test scripts.

MLX_CHAR_W = 10    # pixels per character (horizontal)
MLX_CHAR_H = 13  # pixels per character (vertical)
