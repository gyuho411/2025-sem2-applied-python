import pygame
import tkinter as tk
from tkinter import font as tkfont
import sys
import config
from game_manager import GameManager
from PIL import Image, ImageTk
import cv2  # [필수] opencv-python 설치 필요

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
        self.lock_image = None

        try:
            if image_path:
                loaded_img = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(loaded_img, (w, h))
            if lock_image_path:
                loaded_lock = pygame.image.load(lock_image_path).convert_alpha()
                self.lock_image = pygame.transform.scale(loaded_lock, (w, h))
        except Exception:
            pass

    def draw(self, screen, font, current_money, current_time):
        elapsed_time = current_time - self.last_clicked_time
        on_cooldown = elapsed_time < self.cooldown_ms
        is_money_enough = current_money >= self.cost
        
        if not is_money_enough or on_cooldown:
            if self.lock_image:
                screen.blit(self.lock_image, (self.rect.x, self.rect.y))
            else:
                if self.image: screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            if self.image:
                screen.blit(self.image, (self.rect.x, self.rect.y))

        text_color = config.YELLOW if is_money_enough else config.RED
        shadow_surf = font.render(f"${self.cost}", True, config.BLACK)
        cost_surf = font.render(f"${self.cost}", True, text_color)
        cost_x = self.rect.x + (self.rect.width - cost_surf.get_width()) // 2
        cost_y = self.rect.y + self.rect.height - 25
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
# 텍스트 기반 버튼
# ==========================================
class TextButton:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, config.BLACK, self.rect, 2)
        label = font.render(self.text, True, config.BLACK)
        label_x = self.rect.x + (self.rect.width - label.get_width()) // 2
        label_y = self.rect.y + (self.rect.height - label.get_height()) // 2
        screen.blit(label, (label_x, label_y))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ==========================================
# [함수 정의] 동영상 재생 (수정됨: 원본 속도 유지)
# ==========================================
def play_video(screen, video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[오류] 비디오 파일을 열 수 없습니다: {video_path}")
        return

    # [수정] 원본 영상의 FPS(초당 프레임 수)를 가져옵니다.
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0: fps = 30 # FPS 정보를 읽지 못했다면 기본 30으로 설정

    clock = pygame.time.Clock()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break # 영상 끝
            
        # OpenCV(BGR) -> Pygame(RGB) 변환 및 사이즈 조정
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        video_surf = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")
        
        screen.blit(video_surf, (0, 0))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    cap.release()
                    return 

        # [수정] 원본 FPS에 맞춰서 딜레이를 줍니다.
        clock.tick(fps) 
        
    cap.release()
    screen.fill(config.BLACK)
    pygame.display.flip()

# ==========================================
# 게임 실행 루프
# ==========================================
def run_game(stage_level):
    try:
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        pygame.mixer.init()
    except Exception as e:
        print(f"[오류] 사운드 시스템 초기화 실패: {e}")

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(f"Defense Game - Stage {stage_level}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22, bold=True) 

    gm = GameManager(stage_level)

    # 배경 이미지 로드
    bg_image_path = config.IMG_BACKGROUND
    if stage_level == 1: bg_image_path = getattr(config, 'IMG_BG_STAGE1', config.IMG_BACKGROUND)
    elif stage_level == 2: bg_image_path = getattr(config, 'IMG_BG_STAGE2', config.IMG_BACKGROUND)
    elif stage_level == 3: bg_image_path = getattr(config, 'IMG_BG_STAGE3', config.IMG_BACKGROUND)
    
    current_bg_image = None
    boss_bg_image = None

    try:
        if bg_image_path:
            loaded = pygame.image.load(bg_image_path)
            current_bg_image = pygame.transform.scale(loaded, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    except: pass

    if stage_level == 3:
        boss_path = getattr(config, 'IMG_BG_STAGE3_B', None)
        try:
            if boss_path:
                loaded_boss = pygame.image.load(boss_path)
                boss_bg_image = pygame.transform.scale(loaded_boss, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        except: pass
            
    # 결과 이미지 로드
    img_victory = None
    img_defeat = None
    try:
        v_img = pygame.image.load(config.IMG_RESULT_VIC)
        img_victory = pygame.transform.scale(v_img, (600, 350)) 
        d_img = pygame.image.load(config.IMG_RESULT_DEF)
        img_defeat = pygame.transform.scale(d_img, (600, 350)) 
    except Exception as e:
        print(f"결과 이미지 로드 실패: {e}")

    # 버튼 설정
    path_c1 = getattr(config, 'IMG_BTN_C1', None) 
    path_c2 = getattr(config, 'IMG_BTN_C2', None)
    path_c3 = getattr(config, 'IMG_BTN_C3', None)
    path_c1_lock = getattr(config, 'IMG_BTN_C1_LOCK', None)
    path_c2_lock = getattr(config, 'IMG_BTN_C2_LOCK', None)
    path_c3_lock = getattr(config, 'IMG_BTN_C3_LOCK', None)

    btn_w, btn_h = 120, 120
    btn_y = config.SCREEN_HEIGHT - 130 
    
    btn_c1 = UI_Button(30,            btn_y, btn_w, btn_h, path_c1, lock_image_path=path_c1_lock, cost=50,  cooldown=4.0)
    btn_c2 = UI_Button(30 + 120 + 20, btn_y, btn_w, btn_h, path_c2, lock_image_path=path_c2_lock, cost=100, cooldown=7.0)
    btn_c3 = UI_Button(30 + 240 + 40, btn_y, btn_w, btn_h, path_c3, lock_image_path=path_c3_lock, cost=400, cooldown=10.0)

    btn_retry = TextButton(config.SCREEN_WIDTH//2 - 110, config.SCREEN_HEIGHT//2 + 150, 100, 50, "RETRY", config.WHITE)
    btn_menu = TextButton(config.SCREEN_WIDTH//2 + 10, config.SCREEN_HEIGHT//2 + 150, 100, 50, "MENU", config.WHITE)

    running = True
    next_action = "QUIT"
    video_played = False # 비디오 재생 여부 체크

    # ==============================
    # [1] 게임 플레이 루프
    # ==============================
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
                    if btn_c1.is_clicked(pos) and btn_c1.is_available(gm.money, current_time):
                        if gm.spawn_player_unit(1): btn_c1.use(current_time)
                    elif btn_c2.is_clicked(pos) and btn_c2.is_available(gm.money, current_time):
                        if gm.spawn_player_unit(2): btn_c2.use(current_time)
                    elif btn_c3.is_clicked(pos) and btn_c3.is_available(gm.money, current_time):
                        if gm.spawn_player_unit(3): btn_c3.use(current_time)
                else:
                    if btn_retry.is_clicked(pos):
                        running = False
                        next_action = "RETRY"
                    elif btn_menu.is_clicked(pos):
                        running = False
                        next_action = "MENU"

        if not gm.game_over:
            gm.update(dt_sec, current_time)

        if stage_level == 3 and gm.boss_spawned and boss_bg_image:
            if current_bg_image != boss_bg_image:
                current_bg_image = boss_bg_image

        screen.fill(config.WHITE)
        if current_bg_image: screen.blit(current_bg_image, (0,0))

        gm.enemy_units.draw(screen)
        gm.player_units.draw(screen)
        gm.effects.draw(screen) 
        btn_c1.draw(screen, font, gm.money, current_time)
        btn_c2.draw(screen, font, gm.money, current_time)
        btn_c3.draw(screen, font, gm.money, current_time)
        gm.draw_ui(screen, font)

        # ==============================
        # [2] 게임 종료(클리어) 체크
        # ==============================
        if gm.game_over:
            # (1) 만약 3스테이지고 + 승리했다면 + 아직 비디오를 안 봤다면?
            if stage_level == 3 and "VICTORY" in gm.result_message:
                if not video_played:
                    # ---> 여기서 비디오가 재생됩니다! <---
                    play_video(screen, config.VID_ENDING)
                    video_played = True 
                    
                    # 비디오 끝나고 배경 복구
                    if current_bg_image: screen.blit(current_bg_image, (0,0))

            # (2) 승리/패배 화면 출력
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(config.BLACK)
            screen.blit(overlay, (0,0))

            target_image = None
            if "VICTORY" in gm.result_message:
                target_image = img_victory
            else:
                target_image = img_defeat

            if target_image:
                img_x = config.SCREEN_WIDTH // 2 - target_image.get_width() // 2
                img_y = config.SCREEN_HEIGHT // 2 - target_image.get_height() // 2 - 20
                screen.blit(target_image, (img_x, img_y))

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
        self.canvas = None
        self.enter_item = None
        self.flash_count = 0
        self.max_flashes = 0
        self.overlay_image = None 
        self.is_transitioning = False
        self.load_assets()
        self.show_start_screen()

    def load_assets(self):
        self.img_bg = self.safe_load_image(config.IMG_MENU_BG, (1024, 572))
        self.img_txt_enter = self.safe_load_image(getattr(config, 'IMG_TXT_ENTER', None))
        btn_size = (300, 80)
        self.img_btn_st1 = self.safe_load_image(config.IMG_BTN_STAGE1, btn_size)
        self.img_btn_st2 = self.safe_load_image(config.IMG_BTN_STAGE2, btn_size)
        self.img_btn_st3 = self.safe_load_image(config.IMG_BTN_STAGE3, btn_size)

    def safe_load_image(self, path, resize_to=None):
        if not path: return None
        try:
            img = Image.open(path)
            if resize_to: img = img.resize(resize_to, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception: return None 

    def clear_window(self):
        for widget in self.root.winfo_children(): widget.destroy()

    def create_background_canvas(self):
        canvas = tk.Canvas(self.root, width=1024, height=572, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        if self.img_bg: canvas.create_image(0, 0, image=self.img_bg, anchor="nw")
        else: canvas.configure(bg="#F0F8FF") 
        return canvas

    def show_start_screen(self):
        self.clear_window()
        self.root.bind('<Return>', self.start_flash_effect)
        self.canvas = self.create_background_canvas()
        if self.img_txt_enter: self.enter_item = self.canvas.create_image(512, 480, image=self.img_txt_enter)
        else: self.enter_item = self.canvas.create_text(512, 480, text="PRESS ENTER TO START", font=("Arial", 20, "bold"), fill="black")

    def start_flash_effect(self, event=None):
        self.root.unbind('<Return>') 
        self.flash_count = 0
        self.max_flashes = 14  
        self.run_flash_animation()

    def run_flash_animation(self):
        if not self.enter_item: return
        current_state = self.canvas.itemcget(self.enter_item, 'state')
        new_state = 'hidden' if current_state != 'hidden' else 'normal'
        self.canvas.itemconfig(self.enter_item, state=new_state)
        self.flash_count += 1
        if self.flash_count < self.max_flashes: self.root.after(40, self.run_flash_animation)
        else: self.show_stage_select_screen()

    def show_stage_select_screen(self, event=None):
        self.root.unbind('<Return>')
        self.root.bind('<BackSpace>', self.go_back_to_start)
        self.is_transitioning = False
        self.clear_window()
        canvas = self.create_background_canvas()
        self.canvas = canvas

        if not self.overlay_image:
            overlay = Image.new('RGBA', (1024, 572), (0, 0, 0, 150))
            self.overlay_image = ImageTk.PhotoImage(overlay)
        canvas.create_image(0, 0, image=self.overlay_image, anchor="nw")

        if self.img_btn_st1:
            btn_st1 = tk.Button(self.root, image=self.img_btn_st1, borderwidth=0, highlightthickness=0, activebackground="black", bg="black")
        else: btn_st1 = tk.Button(self.root, text="Stage 1", width=20, height=2, bg="lightgreen")
        win_id_1 = canvas.create_window(512, 300, window=btn_st1)
        btn_st1.config(command=lambda: self.trigger_stage_start(1, win_id_1))

        if self.img_btn_st2:
            btn_st2 = tk.Button(self.root, image=self.img_btn_st2, borderwidth=0, highlightthickness=0, activebackground="black", bg="black")
        else: btn_st2 = tk.Button(self.root, text="Stage 2", width=20, height=2, bg="orange")
        win_id_2 = canvas.create_window(512, 390, window=btn_st2)
        btn_st2.config(command=lambda: self.trigger_stage_start(2, win_id_2))

        if self.img_btn_st3:
            btn_st3 = tk.Button(self.root, image=self.img_btn_st3, borderwidth=0, highlightthickness=0, activebackground="black", bg="black")
        else: btn_st3 = tk.Button(self.root, text="Stage 3", width=20, height=2, bg="purple", fg="white")
        win_id_3 = canvas.create_window(512, 480, window=btn_st3)
        btn_st3.config(command=lambda: self.trigger_stage_start(3, win_id_3))

    def go_back_to_start(self, event=None):
        if self.is_transitioning: return
        self.root.unbind('<BackSpace>')
        self.show_start_screen()

    def trigger_stage_start(self, stage_level, item_id):
        if self.is_transitioning: return
        self.is_transitioning = True
        self.root.unbind('<BackSpace>')
        self.run_stage_flash(stage_level, item_id, 0, 14)

    def run_stage_flash(self, stage_level, item_id, count, max_count):
        current_state = self.canvas.itemcget(item_id, 'state')
        new_state = 'hidden' if current_state != 'hidden' else 'normal'
        self.canvas.itemconfig(item_id, state=new_state)
        count += 1
        if count < max_count: self.root.after(40, lambda: self.run_stage_flash(stage_level, item_id, count, max_count))
        else:
            self.canvas.itemconfig(item_id, state='normal')
            self.launch_game(stage_level)

    def launch_game(self, stage_level):
        self.root.withdraw() 
        try:
            result = run_game(stage_level)
            if result == "RETRY": self.launch_game(stage_level)
            elif result == "MENU":
                self.root.deiconify() 
                self.show_stage_select_screen()
            elif result == "QUIT":
                self.root.destroy()
                sys.exit()
        except Exception as e:
            print(f"게임 실행 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            self.root.deiconify()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GameLauncher()
    app.run()