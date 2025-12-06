import os

# ==============================
# 화면 및 게임 설정
# ==============================
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

# ==============================
# [이미지 경로 통합 관리]
# ==============================
BASE_IMAGE_DIR = r"C:\LGH_kangnam_univ\2025-2\applied_py\2025-sem2-applied-python\image"

def get_path(filename):
    return os.path.join(BASE_IMAGE_DIR, filename)

# 1. 배경 및 UI
IMG_BACKGROUND = get_path("background.png")
IMG_MENU_BG = get_path("menu_bg.png")

IMG_BTN_START = get_path("btn_start.png")
IMG_BTN_EXIT = get_path("btn_exit.png")
IMG_BTN_STAGE1 = get_path("btn_stage1.png")
IMG_BTN_STAGE2 = get_path("btn_stage2.png")
IMG_BTN_STAGE3 = get_path("btn_stage3.png") 
IMG_BTN_BACK = get_path("btn_back.png")
IMG_TXT_ENTER = get_path("txt_enter.png")

# 2. 아군 유닛 (모두 _A 있음)
IMG_C1 = get_path("C-1.png")
IMG_C1_A = get_path("C-1_A.png")

IMG_C2 = get_path("C-2.png")
IMG_C2_A = get_path("C-2_A.png")

IMG_C3 = get_path("C-3.png")
IMG_C3_A = get_path("C-3_A.png")

# 3. 적군 유닛
IMG_M1_1 = get_path("M1-1.png")
IMG_M1_2 = get_path("M1-2.png")

IMG_M2_1 = get_path("M2-1.png")
IMG_M2_1_A = get_path("M2-1_A.png")

IMG_M2_2 = get_path("M2-2.png")
IMG_M2_2_A = get_path("M2-2_A.png")

IMG_MBOSS = get_path("M-Boss.png")
IMG_MBOSS_A = get_path("M-Boss_A.png")

# 4. 아군 사망 승천 이미지
IMG_C_DIE = get_path("C_Die.png")

# ==============================
# 게임 밸런스 설정
# ==============================
PLAYER_BASE_HP = 150
MONEY_RATE = 10
MONEY_INTERVAL = 0.5
MAX_MONEY = 2000