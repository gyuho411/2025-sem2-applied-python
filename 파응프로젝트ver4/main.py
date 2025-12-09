import pygame
import tkinter as tk
from tkinter import font as tkfont
import sys
import config
from game_manager import GameManager

# ==========================================
# 이미지 기반 유닛 소환 버튼
# ==========================================
class UI_Button:
    def __init__(self, x, y, w, h, image_path, lock_image_path=None, cost=0, cooldown=0):
        self.rect = pygame.Rect(x, y, w, h)
        self.cost = cost
        
        self.cooldown_ms = cooldown * 1000  
        self.last_clicked_time = -99999     

        self.image = None
        self.lock_image = None # 잠금(돈 부족/쿨타임) 이미지

        try:
            # 1. 일반 이미지 로드
            if image_path:
                loaded_img = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(loaded_img, (w, h))
            
            # 2. 잠금 이미지 로드
            if lock_image_path:
                loaded_lock = pygame.image.load(lock_image_path).convert_alpha()
                self.lock_image = pygame.transform.scale(loaded_lock, (w, h))
                
        except Exception as e:
            print(f"버튼 이미지 로드 실패: {e}")

    def draw(self, screen, font, current_money, current_time):
        # 상태 계산
        elapsed_time = current_time - self.last_clicked_time
        on_cooldown = elapsed_time < self.cooldown_ms
        is_money_enough = current_money >= self.cost
        
        # ------------------------------------------------------------
        # 1. 이미지 그리기 (일반 vs 잠금)
        # ------------------------------------------------------------
        # 돈이 부족하거나 OR 쿨타임 중일 때 -> Lock 이미지 사용
        if not is_money_enough or on_cooldown:
            if self.lock_image:
                screen.blit(self.lock_image, (self.rect.x, self.rect.y))
            else:
                # 락 이미지가 없으면 일반 이미지라도 그림
                if self.image: screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            # 사용 가능 상태 -> 일반 이미지 사용
            if self.image:
                screen.blit(self.image, (self.rect.x, self.rect.y))

        # [삭제됨] 2. 쿨타임 게이지 그리기 코드 삭제 완료

        # ------------------------------------------------------------
        # 3. 비용 텍스트 표시
        # ------------------------------------------------------------
        text_color = config.YELLOW if is_money_enough else config.RED
        
        shadow_surf = font.render(f"${self.cost}", True, config.BLACK)
        cost_surf = font.render(f"${self.cost}", True, text_color)
        
        cost_x = self.rect.x + (self.rect.width - cost_surf.get_width()) // 2
        cost_y = self.rect.y + self.rect.height + 5
        
        screen.blit(shadow_surf, (cost_x + 1, cost_y + 1))
        screen.blit(cost_surf, (cost_x, cost_y))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def is_available(self, current_money, current_time):
        elapsed = current_time - self.last_clicked_time
        if current_money >= self.cost and elapsed >= self.cooldown_ms:
            return True
        return False

    def use(self, current_time):
        self.last_clicked_time = current_time

# ==========================================
# 텍스트 기반 버튼 (Retry, Menu용)
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
    
    font = pygame.font.SysFont("arial", 22, bold=True) 
    big_font = pygame.font.SysFont("arial", 60, bold=True)

    gm = GameManager(stage_level)

    # 1. 배경 로드
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
    # 일반 이미지 경로
    path_c1 = getattr(config, 'IMG_BTN_C1', None) 
    path_c2 = getattr(config, 'IMG_BTN_C2', None)
    path_c3 = getattr(config, 'IMG_BTN_C3', None)

    # 잠금(Lock) 이미지 경로
    path_c1_lock = getattr(config, 'IMG_BTN_C1_LOCK', None)
    path_c2_lock = getattr(config, 'IMG_BTN_C2_LOCK', None)
    path_c3_lock = getattr(config, 'IMG_BTN_C3_LOCK', None)

    btn_w, btn_h = 120, 120
    btn_y = config.SCREEN_HEIGHT - 150 
    
    # 버튼 인스턴스 생성
    btn_c1 = UI_Button(30,            btn_y, btn_w, btn_h, path_c1, lock_image_path=path_c1_lock, cost=50,  cooldown=4.0)
    btn_c2 = UI_Button(30 + 120 + 20, btn_y, btn_w, btn_h, path_c2, lock_image_path=path_c2_lock, cost=100, cooldown=7.0)
    btn_c3 = UI_Button(30 + 240 + 40, btn_y, btn_w, btn_h, path_c3, lock_image_path=path_c3_lock, cost=400, cooldown=10.0)

    # 결과 화면 버튼
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
                    # 유닛 소환
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
                    if btn_retry.is_clicked(pos):
                        running = False
                        next_action = "RETRY"
                    elif btn_menu.is_clicked(pos):
                        running = False
                        next_action = "MENU"

        if not gm.game_over:
            gm.update(dt_sec, current_time)

        screen.fill(config.WHITE)

        if bg_image:
            screen.blit(bg_image, (0,0))

        gm.enemy_units.draw(screen)
        gm.player_units.draw(screen)
        gm.effects.draw(screen) 

        btn_c1.draw(screen, font, gm.money, current_time)
        btn_c2.draw(screen, font, gm.money, current_time)
        btn_c3.draw(screen, font, gm.money, current_time)

        gm.draw_ui(screen, font)

        if gm.game_over:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(config.BLACK)
            screen.blit(overlay, (0,0))

            color = config.GREEN if "VICTORY" in gm.result_message else config.RED
            res_text = big_font.render(gm.result_message, True, color)
            screen.blit(res_text, (config.SCREEN_WIDTH//2 - res_text.get_width()//2, config.SCREEN_HEIGHT//2 - 50))

            btn_retry.draw(screen, font)
            btn_menu.draw(screen, font)

        pygame.display.flip()

    pygame.quit()
    return next_action

# ==========================================
# Tkinter 게임 런처
# ==========================================
class GameLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kangnam Univ Defense Game")
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
        canvas = tk.Canvas(self.root, width=1024, height=572, highlightthickness=0)
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
            canvas.create_image(512, 480, image=self.img_txt_enter)
        else:
            canvas.create_text(512, 480, text="PRESS ENTER TO START", font=("Arial", 20, "bold"), fill="black")

    def show_stage_select_screen(self, event=None):
        self.root.unbind('<Return>')
        self.clear_window()
        canvas = self.create_background_canvas()

        # 스테이지 1
        if self.img_btn_st1:
            btn_st1 = tk.Button(self.root, image=self.img_btn_st1, borderwidth=0, command=lambda: self.launch_game(1))
        else:
            btn_st1 = tk.Button(self.root, text="Stage 1: 이공관", width=20, height=2, bg="lightgreen", font=self.btn_font, command=lambda: self.launch_game(1))
        canvas.create_window(512, 300, window=btn_st1)

        # 스테이지 2
        if self.img_btn_st2:
            btn_st2 = tk.Button(self.root, image=self.img_btn_st2, borderwidth=0, command=lambda: self.launch_game(2))
        else:
            btn_st2 = tk.Button(self.root, text="Stage 2: 달구지", width=20, height=2, bg="orange", font=self.btn_font, command=lambda: self.launch_game(2))
        canvas.create_window(512, 390, window=btn_st2)

        # 스테이지 3
        if self.img_btn_st3:
            btn_st3 = tk.Button(self.root, image=self.img_btn_st3, borderwidth=0, command=lambda: self.launch_game(3))
        else:
            btn_st3 = tk.Button(self.root, text="Stage 3: 머리띠", width=20, height=2, bg="purple", fg="white", font=self.btn_font, command=lambda: self.launch_game(3))
        canvas.create_window(512, 480, window=btn_st3)


    def launch_game(self, stage_level):
        self.root.withdraw() 
        try:
            result = run_game(stage_level)
            if result == "RETRY":
                self.launch_game(stage_level)
            elif result == "MENU":
                self.root.deiconify() 
                self.show_stage_select_screen()
            elif result == "QUIT":
                self.root.destroy()
                sys.exit()
        except Exception as e:
            print(f"게임 실행 중 오류 발생: {e}")
            self.root.deiconify()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GameLauncher()
    app.run()