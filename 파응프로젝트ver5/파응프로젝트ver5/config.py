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
BASE_IMAGE_DIR = r"C:\Users\wonmo\OneDrive\Desktop\파응프로젝트ver5\image"

def get_path(filename):
    return os.path.join(BASE_IMAGE_DIR, filename)

# 1. 배경 및 UI
IMG_BACKGROUND = get_path("stage.png") 
IMG_MENU_BG = get_path("background.png") 

# 스테이지별 배경
IMG_BG_STAGE1 = get_path("stage1.png")
IMG_BG_STAGE2 = get_path("stage2.png")
IMG_BG_STAGE3 = get_path("stage3.png")
IMG_BG_STAGE3_B = get_path("stage3_B.png")

IMG_BTN_START = get_path("btn_start.png")
IMG_BTN_EXIT = get_path("btn_exit.png")
IMG_BTN_STAGE1 = get_path("btn_stage1.png")
IMG_BTN_STAGE2 = get_path("btn_stage2.png")
IMG_BTN_STAGE3 = get_path("btn_stage3.png") 
IMG_BTN_BACK = get_path("btn_back.png")
IMG_TXT_ENTER = get_path("press_enter.png")

# 2. 아군 유닛
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

# 4. 기타
IMG_C_DIE = get_path("C_Die_.png")
IMG_BTN_C1 = get_path("btn_1.png")
IMG_BTN_C2 = get_path("btn_2.png")
IMG_BTN_C3 = get_path("btn_3.png")
IMG_BTN_C1_LOCK = get_path("btn_1_lock.png")
IMG_BTN_C2_LOCK = get_path("btn_2_lock.png")
IMG_BTN_C3_LOCK = get_path("btn_3_lock.png")
IMG_RESULT_VIC = get_path("victory_1_.png")
IMG_RESULT_DEF = get_path("Defeat_.png")

# ==============================
# [NEW] 미디어 경로 (사운드 & 비디오)
# ==============================
# 사운드 경로
BASE_SOUND_DIR = r"C:\Users\wonmo\OneDrive\Desktop\파응프로젝트ver5\sound"
SND_SWING = os.path.join(BASE_SOUND_DIR, "Swing.wav")

# 비디오 경로
BASE_VIDEO_DIR = r"C:\Users\wonmo\OneDrive\Desktop\파응프로젝트ver5\video"
VID_ENDING = os.path.join(BASE_VIDEO_DIR, "ending.mp4")

# ==============================
# 게임 밸런스 설정
# ==============================
PLAYER_BASE_HP = 150
MONEY_RATE = 10
MONEY_INTERVAL = 0.5
MAX_MONEY = 2000

COOLTIME_C1 = 4.0
COOLTIME_C2 = 7.0
COOLTIME_C3 = 10.0