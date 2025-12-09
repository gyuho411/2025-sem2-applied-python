import pygame
import config
import os

# ==========================================
# [신규 클래스] 사망 승천 이펙트
# ==========================================
class DeathEffect(pygame.sprite.Sprite):
    """캐릭터 사망 시 위로 승천하는 애니메이션 이펙트"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((125, 125), pygame.SRCALPHA)
        try:
            loaded_img = pygame.image.load(config.IMG_C_DIE).convert_alpha()
            self.image = pygame.transform.scale(loaded_img, (150, 150))
        except Exception:
            self.image.fill((255, 255, 255, 128))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y) 
        self.rise_speed = 1.0 
        self.alpha = 255       
        self.fade_speed = 0.8

    def update(self, dt_sec):
        self.rect.y -= self.rise_speed
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(int(self.alpha))

# ==========================================
# 1. 기본 엔티티 클래스 (부모)
# ==========================================
class GameEntity(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, speed, attack_power, attack_range, attack_speed, team, image_path, attack_image_path, on_death_callback=None):
        super().__init__()

        self.team = team
        self.state = "move"
        self.on_death_callback = on_death_callback

        default_surface = pygame.Surface((125, 125))
        default_surface.fill(config.BLUE if team == 'player' else config.RED)

        self.base_image = default_surface.copy()
        self.attack_image = default_surface.copy()

        self.load_and_set_image(image_path, is_attack=False)
        self.load_and_set_image(attack_image_path, is_attack=True)

        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        self.exact_x = float(self.rect.x)

        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.attack_power = attack_power
        self.attack_range = attack_range

        self.attack_cooldown = attack_speed * 1000 
        self.last_attack_time = 0

        self.attack_anim_start_time = 0 
        self.anim_duration = 200

        # [NEW] 아군 공격 사운드 로드
        self.swing_sound = None
        if self.team == 'player':
            try:
                # 파일이 실제로 존재하는지 확인 (디버깅용)
                if os.path.exists(config.SND_SWING):
                    self.swing_sound = pygame.mixer.Sound(config.SND_SWING)
                    self.swing_sound.set_volume(0.4) # 볼륨 조절 (0.0 ~ 1.0)
                    # print(f"[알림] 사운드 로드 성공: {config.SND_SWING}")
                else:
                    print(f"[경고] 사운드 파일이 없습니다: {config.SND_SWING}")
            except Exception as e:
                print(f"[오류] 사운드 로드 중 에러 발생: {e}")

    def load_and_set_image(self, path, is_attack):
        try:
            loaded_img = pygame.image.load(path)
            if "Boss" in path:
                target_size = (375, 375) 
            else:
                target_size = (150, 150) 
            scaled_img = pygame.transform.scale(loaded_img, target_size)
            if is_attack:
                self.attack_image = scaled_img
            else:
                self.base_image = scaled_img
        except Exception:
            pass 

    def update(self, target_list, current_time):
        if self.hp <= 0:
            if self.team == 'player' and self.on_death_callback:
                self.on_death_callback(self.rect.centerx, self.rect.centery)
            self.kill()
            return

        target = self.find_nearest_target(target_list)

        if target:
            distance = abs(self.rect.centerx - target.rect.centerx)
            if distance <= self.attack_range:
                self.state = "attack"
                self.attack(target, current_time)
            else:
                self.state = "move"
                self.move()
        else:
            self.state = "move"
            self.move()

        if current_time - self.attack_anim_start_time < self.anim_duration:
            self.image = self.attack_image
        else:
            self.image = self.base_image

    def move(self):
        direction = 1 if self.team == 'player' else -1
        self.exact_x += self.speed * direction
        self.rect.x = int(self.exact_x)

    def find_nearest_target(self, target_list):
        nearest = None
        min_dist = float('inf')
        for unit in target_list:
            dist = abs(self.rect.centerx - unit.rect.centerx)
            if dist < min_dist:
                min_dist = dist
                nearest = unit
        return nearest

    def attack(self, target, current_time):
        if current_time - self.last_attack_time >= self.attack_cooldown:
            target.take_damage(self.attack_power)
            self.last_attack_time = current_time
            self.attack_anim_start_time = current_time
            
            # [NEW] 아군이면 공격 사운드 재생
            if self.swing_sound:
                self.swing_sound.play()

    def take_damage(self, amount):
        self.hp -= amount

# ==========================================
# 2. 팀별 중간 부모 클래스
# ==========================================
class PlayerUnit(GameEntity):
    def __init__(self, x, y, hp, speed, atk, rng, atk_spd, cost, spawn_delay, image_path, attack_image_path, on_death_callback):
        super().__init__(x, y, hp, speed, atk, rng, atk_spd, 'player', image_path, attack_image_path, on_death_callback)
        self.cost = cost
        self.spawn_delay = spawn_delay

class EnemyUnit(GameEntity):
    def __init__(self, x, y, hp, speed, atk, rng, atk_spd, image_path, attack_image_path):
        super().__init__(x, y, hp, speed, atk, rng, atk_spd, 'enemy', image_path, attack_image_path, None)

# ==========================================
# 3. 개별 캐릭터 상세 정의
# ==========================================

# --- [아군] ---
class C1(PlayerUnit):
    def __init__(self, x, y, on_death_callback):
        super().__init__(x, y, hp=100, speed=1.5, atk=2000, rng=100, atk_spd=0.8, cost=50, spawn_delay=4.0, image_path=config.IMG_C1, attack_image_path=config.IMG_C1_A, on_death_callback=on_death_callback)

class C2(PlayerUnit):
    def __init__(self, x, y, on_death_callback):
        super().__init__(x, y, hp=400, speed=0.8, atk=10, rng=90, atk_spd=0.8, cost=100, spawn_delay=7.0, image_path=config.IMG_C2, attack_image_path=config.IMG_C2_A, on_death_callback=on_death_callback)

class C3(PlayerUnit):
    def __init__(self, x, y, on_death_callback):
        super().__init__(x, y, hp=200, speed=1.2, atk=40, rng=125, atk_spd=1.0, cost=400, spawn_delay=10.0, image_path=config.IMG_C3, attack_image_path=config.IMG_C3_A, on_death_callback=on_death_callback)

# --- [적군] ---
class M1_1(EnemyUnit):
    def __init__(self, x, y):
        super().__init__(x, y, hp=60, speed=1.0, atk=8, rng=80, atk_spd=1.0, image_path=config.IMG_M1_1, attack_image_path=config.IMG_M1_1)

class M1_2(EnemyUnit):
    def __init__(self, x, y):
        super().__init__(x, y, hp=90, speed=2.0, atk=12, rng=80, atk_spd=0.8, image_path=config.IMG_M1_2, attack_image_path=config.IMG_M1_2)

class M2_1(EnemyUnit):
    def __init__(self, x, y):
        super().__init__(x, y, hp=250, speed=0.5, atk=20, rng=100, atk_spd=1.2, image_path=config.IMG_M2_1, attack_image_path=config.IMG_M2_1_A)

class M2_2(EnemyUnit):
    def __init__(self, x, y):
        super().__init__(x, y, hp=300, speed=1.1, atk=25, rng=115, atk_spd=2.0, image_path=config.IMG_M2_2, attack_image_path=config.IMG_M2_2_A)

class MBoss(EnemyUnit):
    def __init__(self, x, y):
        super().__init__(x, y, hp=3000, speed=0.4, atk=100, rng=160, atk_spd=2, image_path=config.IMG_MBOSS, attack_image_path=config.IMG_MBOSS_A)