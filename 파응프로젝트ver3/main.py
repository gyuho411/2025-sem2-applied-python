import pygame
import tkinter as tk
from tkinter import font as tkfont
import sys
import config
from game_manager import GameManager

# ==========================================
# [수정] 이미지 기반 유닛 소환 버튼
# ==========================================
class UI_Button:
    def __init__(self, x, y, w, h, image_path, cost=0, cooldown=0):
        self.rect = pygame.Rect(x, y, w, h)
        self.cost = cost
        
        # 쿨타임 관련 변수
        self.cooldown_ms = cooldown * 1000  # 초 -> 밀리초
        self.last_clicked_time = -99999     # 초기엔 바로 사용 가능

        # 이미지 로드 및 크기 조정
        self.image = None
        try:
            # config에 경로가 없거나 파일이 없으면 예외 처리
            if image_path:
                loaded_img = pygame.image.load(image_path)
                self.image = pygame.transform.scale(loaded_img, (w, h))
        except Exception as e:
            print(f"버튼 이미지 로드 실패 ({image_path}): {e}")
            self.image = None

    def draw(self, screen, font, current_money, current_time):
        # 1. 기본 버튼 그리기 (이미지 or 회색 박스)
        if self.image:
            screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, config.GRAY, self.rect)
        
        # 테두리
        pygame.draw.rect(screen, config.BLACK, self.rect, 2)

        # 상태 계산
        elapsed_time = current_time - self.last_clicked_time
        on_cooldown = elapsed_time < self.cooldown_ms
        is_money_enough = current_money >= self.cost

        # 2. [돈 부족] 상태: 전체를 어둡게 처리
        if not is_money_enough:
            overlay = pygame.Surface((self.rect.width, self.rect.height))
            overlay.set_alpha(180) # 0~255 (높을수록 어두움)
            overlay.fill((50, 50, 50)) 
            screen.blit(overlay, (self.rect.x, self.rect.y))

        # 3. [쿨타임] 상태: 아래에서 위로 차오르는 효과
        if on_cooldown:
            # 남은 시간 비율 (1.0 -> 0.0)
            ratio = 1.0 - (elapsed_time / self.cooldown_ms)
            height = int(self.rect.height * ratio)
            
            # 쿨타임 게이지 (검은색 반투명)
            s = pygame.Surface((self.rect.width, height))
            s.set_alpha(200)
            s.fill((0, 0, 0))
            # 버튼 하단부터 차오르게 배치
            screen.blit(s, (self.rect.x, self.rect.y + (self.rect.height - height)))

        # 4. 비용 텍스트 표시
        if self.cost > 0:
            text_color = config.YELLOW if is_money_enough else config.RED
            cost_surf = font.render(f"${self.cost}", True, text_color)
            
            # 텍스트 위치: 버튼 하단 중앙
            cost_x = self.rect.x + (self.rect.width - cost_surf.get_width()) // 2
            cost_y = self.rect.y + self.rect.height + 5
            screen.blit(cost_surf, (cost_x, cost_y))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def is_available(self, current_money, current_time):
        """돈도 있고 쿨타임도 끝났는지 확인"""
        elapsed = current_time - self.last_clicked_time
        if current_money >= self.cost and elapsed >= self.cooldown_ms:
            return True
        return False

    def use(self, current_time):
        """사용 처리 (쿨타임 시작)"""
        self.last_clicked_time = current_time


# ==========================================
# [추가] 텍스트 기반 버튼 (Retry, Menu용)
# ==========================================
class TextButton:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, config.BLACK, self.rect, 2)
        
        label = font.render(self.text, True, config.WHITE)
        label_x = self.rect.x + (self.rect.width - label.get_width()) // 2
        label_y = self.rect.y + (self.rect.height - label.get_height()) // 2
        screen.blit(label, (label_x, label_y))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ==========================================
# 게임 실행 루프
# ==========================================
def run_game(stage_level):
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(f"Defense Game - Stage {stage_level}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20, bold=True) 
    big_font = pygame.font.SysFont("arial", 60, bold=True)

    gm = GameManager(stage_level)

    # 1. 배경 이미지 로드 (스테이지별)
    bg_image_path = config.IMG_BACKGROUND
    if stage_level == 1: 
        bg_image_path = getattr(config, 'IMG_BG_STAGE1', config.IMG_BACKGROUND)
    elif stage_level == 2: 
        bg_image_path = getattr(config, 'IMG_BG_STAGE2', config.IMG_BACKGROUND)
    elif stage_level == 3: 
        bg_image_path = getattr(config, 'IMG_BG_STAGE3', config.IMG_BACKGROUND)
    
    bg_image = None
    try:
        loaded = pygame.image.load(bg_image_path)
        bg_image = pygame.transform.scale(loaded, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    except:
        pass

    # 2. 버튼 생성
    # config에 IMG_BTN_C1 등의 경로가 정의되어 있어야 합니다.
    # 정의가 안되어 있다면 안전하게 getattr로 처리하거나 직접 문자열을 넣으세요.
    path_c1 = getattr(config, 'IMG_BTN_C1', None) 
    path_c2 = getattr(config, 'IMG_BTN_C2', None)
    path_c3 = getattr(config, 'IMG_BTN_C3', None)

    # 쿨타임 값도 config에서 가져오거나 기본값 사용
    cool_c1 = getattr(config, 'COOLTIME_C1', 5.0)
    cool_c2 = getattr(config, 'COOLTIME_C2', 10.0)
    cool_c3 = getattr(config, 'COOLTIME_C3', 15.0)

    # UI_Button(x, y, w, h, 이미지경로, 가격, 쿨타임)
    btn_c1 = UI_Button(20, config.SCREEN_HEIGHT - 90, 100, 70, path_c1, 50, cool_c1)
    btn_c2 = UI_Button(130, config.SCREEN_HEIGHT - 90, 100, 70, path_c2, 150, cool_c2)
    btn_c3 = UI_Button(240, config.SCREEN_HEIGHT - 90, 100, 70, path_c3, 400, cool_c3)

    # 결과 화면 버튼 (TextButton 사용)
    btn_retry = TextButton(config.SCREEN_WIDTH//2 - 110, config.SCREEN_HEIGHT//2 + 50, 100, 50, "RETRY", config.GREEN)
    btn_menu = TextButton(config.SCREEN_WIDTH//2 + 10, config.SCREEN_HEIGHT//2 + 50, 100, 50, "MENU", config.RED)

    running = True
    next_action = "QUIT"

    while running:
        dt = clock.tick(config.FPS)
        dt_sec = dt / 1000.0
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                next_action = "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if not gm.game_over:
                    # 유닛 소환 버튼 클릭 처리
                    if btn_c1.is_clicked(pos) and btn_c1.is_available(gm.money, current_time):
                        if gm.spawn_player_unit(1): 
                            btn_c1.use(current_time)

                    elif btn_c2.is_clicked(pos) and btn_c2.is_available(gm.money, current_time):
                        if gm.spawn_player_unit(2): 
                            btn_c2.use(current_time)

                    elif btn_c3.is_clicked(pos) and btn_c3.is_available(gm.money, current_time):
                        if gm.spawn_player_unit(3): 
                            btn_c3.use(current_time)
                else:
                    # 결과 화면 버튼 클릭 처리
                    if btn_retry.is_clicked(pos):
                        running = False
                        next_action = "RETRY"
                    elif btn_menu.is_clicked(pos):
                        running = False
                        next_action = "MENU"

        if not gm.game_over:
            gm.update(dt_sec, current_time)

        screen.fill(config.WHITE)

        # 배경 그리기
        if bg_image:
            screen.blit(bg_image, (0,0))

        # 게임 요소 그리기
        gm.enemy_units.draw(screen)
        gm.player_units.draw(screen)
        gm.effects.draw(screen) 

        # 버튼 그리기 (이미지 버튼)
        btn_c1.draw(screen, font, gm.money, current_time)
        btn_c2.draw(screen, font, gm.money, current_time)
        btn_c3.draw(screen, font, gm.money, current_time)

        # UI 텍스트(체력, 돈 등) 그리기
        gm.draw_ui(screen, font)

        # 게임 오버 / 승리 화면
        if gm.game_over:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(config.BLACK)
            screen.blit(overlay, (0,0))

            color = config.GREEN if "VICTORY" in gm.result_message else config.RED
            res_text = big_font.render(gm.result_message, True, color)
            screen.blit(res_text, (config.SCREEN_WIDTH//2 - res_text.get_width()//2, config.SCREEN_HEIGHT//2 - 50))

            # 텍스트 버튼 그리기
            btn_retry.draw(screen, font)
            btn_menu.draw(screen, font)

        pygame.display.flip()

    pygame.quit()
    return next_action


# ==========================================
# Tkinter 게임 런처 (기존 유지)
# ==========================================
class GameLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("pygame")
        self.root.geometry("1024x572") 
        self.root.resizable(False, False)

        self.title_font = tkfont.Font(family="Helvetica", size=30, weight="bold")
        self.btn_font = tkfont.Font(family="Helvetica", size=12, weight="bold")

        self.load_assets()
        self.show_start_screen()

    def load_assets(self):
        self.img_bg = self.safe_load_image(config.IMG_MENU_BG)
        self.img_btn_start = self.safe_load_image(config.IMG_BTN_START)
        self.img_btn_exit = self.safe_load_image(config.IMG_BTN_EXIT)
        self.img_btn_st1 = self.safe_load_image(config.IMG_BTN_STAGE1)
        self.img_btn_st2 = self.safe_load_image(config.IMG_BTN_STAGE2)

        st3_path = getattr(config, 'IMG_BTN_STAGE3', None)
        self.img_btn_st3 = self.safe_load_image(st3_path) if st3_path else None

        txt_enter_path = getattr(config, 'IMG_TXT_ENTER', None)
        self.img_txt_enter = self.safe_load_image(txt_enter_path) if txt_enter_path else None

        self.img_btn_back = self.safe_load_image(config.IMG_BTN_BACK)

    def safe_load_image(self, path):
        if not path: return None
        try:
            return tk.PhotoImage(file=path)
        except:
            return None 

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_background_canvas(self):
        canvas = tk.Canvas(self.root, width=500, height=500, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        if self.img_bg:
            canvas.create_image(0, 0, image=self.img_bg, anchor="nw")
        else:
            canvas.configure(bg="#F0F8FF") 
        return canvas

    def show_start_screen(self):
        self.clear_window()
        self.root.bind('<Return>', self.show_stage_select_screen)
        canvas = self.create_background_canvas()
        
        if self.img_txt_enter:
            canvas.create_image(500, 480, image=self.img_txt_enter)
        else:
            canvas.create_text(500, 480, text="(Press Enter)", font=("Arial", 15, "bold"), fill="gray")

    def show_stage_select_screen(self, event=None):
        self.root.unbind('<Return>')
        self.clear_window()
        canvas = self.create_background_canvas()

        if self.img_btn_st1:
            btn_st1 = tk.Button(self.root, image=self.img_btn_st1, borderwidth=0, command=lambda: self.launch_game(1))
        else:
            btn_st1 = tk.Button(self.root, text="Stage 1: 이공관", width=20, height=2, bg="lightgreen", font=self.btn_font, command=lambda: self.launch_game(1))
        canvas.create_window(500, 300, window=btn_st1)

        if self.img_btn_st2:
            btn_st2 = tk.Button(self.root, image=self.img_btn_st2, borderwidth=0, command=lambda: self.launch_game(2))
        else:
            btn_st2 = tk.Button(self.root, text="Stage 2: 달구지", width=20, height=2, bg="orange", font=self.btn_font, command=lambda: self.launch_game(2))
        canvas.create_window(500, 390, window=btn_st2)

        if self.img_btn_st3:
            btn_st3 = tk.Button(self.root, image=self.img_btn_st3, borderwidth=0, command=lambda: self.launch_game(3))
        else:
            btn_st3 = tk.Button(self.root, text="Stage 3: 머리띠", width=20, height=2, bg="purple", fg="white", font=self.btn_font, command=lambda: self.launch_game(3))
        canvas.create_window(500, 480, window=btn_st3)


    def launch_game(self, stage_level):
        self.root.withdraw() 
        result = run_game(stage_level)
        if result == "RETRY":
            self.launch_game(stage_level)
        elif result == "MENU":
            self.root.deiconify() 
            self.show_stage_select_screen()
        elif result == "QUIT":
            self.root.destroy()
            sys.exit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GameLauncher()
    app.run()