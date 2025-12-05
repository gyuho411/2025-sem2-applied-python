import pygame
import tkinter as tk
from tkinter import font as tkfont
import sys
import config
from game_manager import GameManager

# Pygame 인게임 로직
class UI_Button:
    def __init__(self, x, y, w, h, text, cost=0, color=config.GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.cost = cost
        self.base_color = color
        
    def draw(self, screen, font, current_money=99999):
        is_active = True
        if self.cost > 0:
            is_active = (current_money >= self.cost)
            color = config.BLUE if is_active else config.GRAY
        else:
            color = self.base_color

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, config.BLACK, self.rect, 2)
        
        label = font.render(f"{self.text}", True, config.WHITE)
        text_x = self.rect.x + (self.rect.width - label.get_width()) // 2
        text_y = self.rect.y + 5
        screen.blit(label, (text_x, text_y))
        
        if self.cost > 0:
            cost_label = font.render(f"${self.cost}", True, config.YELLOW)
            cost_x = self.rect.x + (self.rect.width - cost_label.get_width()) // 2
            screen.blit(cost_label, (cost_x, text_y + 25))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def run_game(stage_level):
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(f"Defense Game - Stage {stage_level}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20, bold=True) # 폰트 살짝 줄임
    big_font = pygame.font.SysFont("arial", 60, bold=True)

    gm = GameManager(stage_level)

    # [변경] 버튼 3개 생성 (C1, C2, C3)
    btn_c1 = UI_Button(20, config.SCREEN_HEIGHT - 90, 100, 70, "Soldier", 50)
    btn_c2 = UI_Button(130, config.SCREEN_HEIGHT - 90, 100, 70, "Tank", 200)
    btn_c3 = UI_Button(240, config.SCREEN_HEIGHT - 90, 100, 70, "Sniper", 500)
    
    # 결과창 버튼
    btn_retry = UI_Button(config.SCREEN_WIDTH//2 - 110, config.SCREEN_HEIGHT//2 + 50, 100, 50, "RETRY", 0, config.GREEN)
    btn_menu = UI_Button(config.SCREEN_WIDTH//2 + 10, config.SCREEN_HEIGHT//2 + 50, 100, 50, "MENU", 0, config.RED)

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
                    # [변경] 버튼 클릭 이벤트 연결
                    if btn_c1.is_clicked(pos): gm.spawn_player_unit(1)
                    elif btn_c2.is_clicked(pos): gm.spawn_player_unit(2)
                    elif btn_c3.is_clicked(pos): gm.spawn_player_unit(3)
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
        
        try:
            bg = pygame.image.load(config.IMG_BACKGROUND)
            screen.blit(bg, (0,0))
        except: 
            pass 

        gm.player_units.draw(screen)
        gm.enemy_units.draw(screen)

        # [변경] 버튼 3개 그리기
        btn_c1.draw(screen, font, gm.money)
        btn_c2.draw(screen, font, gm.money)
        btn_c3.draw(screen, font, gm.money)
        
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

# Tkinter 게임 런처
class GameLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("냥코 디펜스 게임")
        self.root.geometry("500x400")
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
        self.img_btn_back = self.safe_load_image(config.IMG_BTN_BACK)

    def safe_load_image(self, path):
        try:
            return tk.PhotoImage(file=path)
        except:
            return None 

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_background_canvas(self):
        canvas = tk.Canvas(self.root, width=500, height=400, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        if self.img_bg:
            canvas.create_image(0, 0, image=self.img_bg, anchor="nw")
        else:
            canvas.configure(bg="#F0F8FF") 
        return canvas

    def show_start_screen(self):
        self.clear_window()
        canvas = self.create_background_canvas()
        canvas.create_text(250, 80, text="파응\n프로젝트", font=self.title_font, fill="darkblue", justify="center")

        if self.img_btn_start:
            btn_start = tk.Button(self.root, image=self.img_btn_start, borderwidth=0, command=self.show_stage_select_screen)
        else:
            btn_start = tk.Button(self.root, text="게임 시작", font=self.btn_font, width=15, height=2, bg="white", fg="blue", command=self.show_stage_select_screen)
        canvas.create_window(250, 200, window=btn_start)

        if self.img_btn_exit:
            btn_exit = tk.Button(self.root, image=self.img_btn_exit, borderwidth=0, command=self.root.destroy)
        else:
            btn_exit = tk.Button(self.root, text="종료", font=self.btn_font, width=15, height=1, bg="white", fg="red", command=self.root.destroy)
        canvas.create_window(250, 300, window=btn_exit)

    def show_stage_select_screen(self):
        self.clear_window()
        canvas = self.create_background_canvas()
        canvas.create_text(250, 50, text="스테이지 선택", font=("Arial", 20, "bold"), fill="black")

        if self.img_btn_st1:
            btn_st1 = tk.Button(self.root, image=self.img_btn_st1, borderwidth=0, command=lambda: self.launch_game(1))
        else:
            btn_st1 = tk.Button(self.root, text="Stage 1: 숲", width=20, height=2, bg="lightgreen", font=self.btn_font, command=lambda: self.launch_game(1))
        canvas.create_window(250, 150, window=btn_st1)

        if self.img_btn_st2:
            btn_st2 = tk.Button(self.root, image=self.img_btn_st2, borderwidth=0, command=lambda: self.launch_game(2))
        else:
            btn_st2 = tk.Button(self.root, text="Stage 2: 사막", width=20, height=2, bg="orange", font=self.btn_font, command=lambda: self.launch_game(2))
        canvas.create_window(250, 250, window=btn_st2)

        if self.img_btn_back:
            btn_back = tk.Button(self.root, image=self.img_btn_back, borderwidth=0, command=self.show_start_screen)
        else:
            btn_back = tk.Button(self.root, text="< 뒤로가기", width=15, height=1, bg="lightgray", command=self.show_start_screen)
        canvas.create_window(250, 350, window=btn_back)

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