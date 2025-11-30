import pygame

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
# [이미지 경로 설정]
# 파일이 없어도 괜찮습니다. 코드가 알아서 기본 모양으로 보여줍니다.
# ==============================

# 1. 인게임용 (Pygame)
IMG_BACKGROUND = "images/background.png"
IMG_PLAYER_UNIT_1 = "images/cat_fighter.png"
IMG_PLAYER_UNIT_2 = "images/cat_tank.png"
IMG_ENEMY_UNIT_1 = "images/doge.png"

# 2. 메뉴용 (Tkinter)
IMG_MENU_BG = "images/menu_bg.png"          
IMG_BTN_START = "images/btn_start.png"      
IMG_BTN_EXIT = "images/btn_exit.png"       
IMG_BTN_STAGE1 = "images/btn_stage1.png"    
IMG_BTN_STAGE2 = "images/btn_stage2.png"   
IMG_BTN_BACK = "images/btn_back.png"       

# ==============================
# 게임 밸런스 설정
# ==============================
PLAYER_BASE_HP = 500  # 내 기지 체력
MONEY_RATE = 10       # 초당 증가하는 돈
MONEY_INTERVAL = 0.5  # 돈 증가 간격(초)
MAX_MONEY = 2000