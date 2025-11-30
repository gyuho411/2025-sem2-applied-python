import pygame
import config
# [변경] 새 캐릭터들 import
from entity import C1, C2, C3, M1_1, M1_2, M2_1, M2_2, MBoss
import random

class GameManager:
    def __init__(self, stage_level):
        self.stage_level = stage_level
        
        # [경제 시스템]
        self.money = 0
        self.money_timer = 0
        
        # [게임 상태: 기지 HP]
        self.player_base_hp = config.PLAYER_BASE_HP
        self.game_over = False
        self.result_message = ""

        # [유닛 그룹]
        self.player_units = pygame.sprite.Group()
        self.enemy_units = pygame.sprite.Group()

        # [웨이브 관리]
        self.total_enemies_to_spawn = 5 + (stage_level * 5) 
        self.enemies_spawned_count = 0
        self.spawn_timer = 0
        self.spawn_interval = 3000 

    def update(self, dt_sec, current_time):
        if self.game_over: return

        # 1. [경제] 돈 자동 증가
        self.money_timer += dt_sec
        if self.money_timer >= config.MONEY_INTERVAL:
            if self.money < config.MAX_MONEY:
                self.money += config.MONEY_RATE
            self.money_timer = 0

        # 2. [시스템] 적 자동 생성 (웨이브)
        if self.enemies_spawned_count < self.total_enemies_to_spawn:
            if current_time - self.spawn_timer > self.spawn_interval:
                self.spawn_enemy()
                self.spawn_timer = current_time
                self.spawn_interval = random.randint(2000, 5000)

        # 3. 유닛 업데이트 및 충돌 처리
        self.player_units.update(self.enemy_units, current_time)
        self.enemy_units.update(self.player_units, current_time)

        # 4. 승패 판정
        self.check_game_status()

    def spawn_player_unit(self, unit_type):
        """[UI -> 로직] 버튼 클릭 시 호출 (C1, C2, C3)"""
        spawn_x, spawn_y = 100, config.SCREEN_HEIGHT - 100
        
        new_unit = None
        # [변경] 번호에 따라 C1, C2, C3 생성
        if unit_type == 1:
            new_unit = C1(spawn_x, spawn_y)
        elif unit_type == 2:
            new_unit = C2(spawn_x, spawn_y)
        elif unit_type == 3:
            new_unit = C3(spawn_x, spawn_y)

        if new_unit:
            # 돈 확인
            if self.money >= new_unit.cost:
                self.money -= new_unit.cost
                self.player_units.add(new_unit)
                return True
        return False

    def spawn_enemy(self):
        """[시스템] 적 생성 로직 - 랜덤 소환"""
        spawn_x, spawn_y = config.SCREEN_WIDTH - 50, config.SCREEN_HEIGHT - 100
        
        # [변경] 적 목록에서 랜덤하게 하나 뽑음 (보스는 마지막 웨이브에 나오게 하거나 확률 조정 가능)
        # 지금은 테스트를 위해 M1_1, M1_2, M2_1 중 랜덤 등장
        enemy_class = random.choice([M1_1, M1_2, M2_1])
        
        # (옵션) 만약 마지막 적이라면 보스 소환?
        if self.enemies_spawned_count == self.total_enemies_to_spawn - 1:
             enemy_class = MBoss

        enemy = enemy_class(spawn_x, spawn_y)
        self.enemy_units.add(enemy)
        self.enemies_spawned_count += 1

    def check_game_status(self):
        """승리/패배 조건 검사"""
        # 패배: 적이 기지 도달
        for enemy in self.enemy_units:
            if enemy.rect.right < 0:
                self.player_base_hp -= 50 
                enemy.kill() 
        
        if self.player_base_hp <= 0:
            self.game_over = True
            self.result_message = "DEFEAT..."

        # 승리: 모든 적 소환 끝 + 필드에 적 없음
        if (self.enemies_spawned_count >= self.total_enemies_to_spawn) and (len(self.enemy_units) == 0):
            self.game_over = True
            self.result_message = "VICTORY!!"

    def draw_ui(self, screen, font):
        # 기지 HP
        pygame.draw.rect(screen, config.RED, (20, 20, 200, 20)) 
        hp_ratio = max(0, self.player_base_hp / config.PLAYER_BASE_HP)
        pygame.draw.rect(screen, config.GREEN, (20, 20, 200 * hp_ratio, 20)) 
        
        hp_text = font.render(f"Base HP: {self.player_base_hp}", True, config.BLACK)
        screen.blit(hp_text, (230, 20))

        # 돈 표시
        money_text = font.render(f"Money: {self.money} / {config.MAX_MONEY}", True, config.BLACK)
        screen.blit(money_text, (20, 50))

        # 남은 적 표시
        remaining = self.total_enemies_to_spawn - self.enemies_spawned_count + len(self.enemy_units)
        wave_text = font.render(f"Enemies Left: {remaining}", True, config.RED)
        screen.blit(wave_text, (config.SCREEN_WIDTH - 250, 20))

        # 결과창
        if self.game_over:
            big_font = pygame.font.SysFont(None, 100)
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(config.BLACK)
            screen.blit(overlay, (0,0))
            
            color = config.GREEN if "VICTORY" in self.result_message else config.RED
            res_text = big_font.render(self.result_message, True, color)
            screen.blit(res_text, (config.SCREEN_WIDTH//2 - res_text.get_width()//2, config.SCREEN_HEIGHT//2 - 50))