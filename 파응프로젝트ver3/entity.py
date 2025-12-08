import pygame
import config

# ==========================================
# [신규 클래스] 사망 승천 이펙트 (설정 유지)
# ==========================================
class DeathEffect(pygame.sprite.Sprite):
    """캐릭터 사망 시 위로 승천하는 애니메이션 이펙트"""
    def __init__(self, x, y):
        super().__init__()
        # 기본 박스 크기 2.5배 (125x125)
        self.image = pygame.Surface((125, 125), pygame.SRCALPHA)

        try:
            loaded_img = pygame.image.load(config.IMG_C_DIE).convert_alpha()
            # 이미지 크기 2.5배 (150x150)
            self.image = pygame.transform.scale(loaded_img, (150, 150))
        except Exception:
            self.image.fill((255, 255, 255, 128))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y) 

        # 속도 설정 (느리게)
        self.rise_speed = 1.0 
        self.alpha = 255       
        self.fade_speed = 0.3  

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

        # 기본 박스 크기 2.5배 (125x125)
        default_surface = pygame.Surface((125, 125))
        default_surface.fill(config.BLUE if team == 'player' else config.RED)

        self.base_image = default_surface.copy()
        self.attack_image = default_surface.copy()

        self.load_and_set_image(image_path, is_attack=False)
        self.load_and_set_image(attack_image_path, is_attack=True)

        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        # [추가] 소수점 이동을 위한 정밀 좌표 변수
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

    def load_and_set_image(self, path, is_attack):
        try:
            loaded_img = pygame.image.load(path)
            # 유닛 크기 2.5배 확대 유지
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

        # [수정] 소수점 좌표를 사용하여 부드럽게 이동
        self.exact_x += self.speed * direction
        self.rect.x = int(self.exact_x) # 실제 화면 좌표(정수)에 반영

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
# 3. 개별 캐릭터 상세 정의 (속도 대폭 감소)
# ==========================================

# --- [아군] ---

class C1(PlayerUnit): #엔티티 설정의 표준
    def __init__(self, x, y, on_death_callback):
        super().__init__(
            x, y,
            hp=100, 
            speed=1.5, # 기존 3.0 -> 1.5
            atk=15, rng=100, atk_spd=0.8,
            cost=50, spawn_delay=1.0,
            image_path=config.IMG_C1,        
            attack_image_path=config.IMG_C1_A,
            on_death_callback=on_death_callback
        )

class C2(PlayerUnit):
    def __init__(self, x, y, on_death_callback):
        super().__init__(
            x, y,
            hp=400, 
            speed=0.6, # 기존 1.0 -> 0.6
            atk=10, rng=80, atk_spd=1.5,
            cost=150, spawn_delay=3.0,
            image_path=config.IMG_C2,
            attack_image_path=config.IMG_C2_A,
            on_death_callback=on_death_callback
        )

class C3(PlayerUnit):
    def __init__(self, x, y, on_death_callback):
        super().__init__(
            x, y,
            hp=80, 
            speed=0.8, # 기존 2.0 -> 0.8
            atk=40, rng=500, atk_spd=2.0,
            cost=400, spawn_delay=5.0,
            image_path=config.IMG_C3,
            attack_image_path=config.IMG_C3_A,
            on_death_callback=on_death_callback
        )

# --- [적군] ---

class M1_1(EnemyUnit):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=60, 
            speed=1.0, # 기존 2.0 -> 1.0
            atk=8, rng=80, atk_spd=1.0,
            image_path=config.IMG_M1_1,
            attack_image_path=config.IMG_M1_1 
        )

class M1_2(EnemyUnit):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=90, 
            speed=2.0, # 기존 4.0 -> 2.0
            atk=12, rng=80, atk_spd=0.8,
            image_path=config.IMG_M1_2,
            attack_image_path=config.IMG_M1_2 
        )

class M2_1(EnemyUnit):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=250, 
            speed=0.6, # 기존 1.0 -> 0.6
            atk=20, rng=100, atk_spd=1.5,
            image_path=config.IMG_M2_1,
            attack_image_path=config.IMG_M2_1_A
        )

class M2_2(EnemyUnit):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=200, 
            speed=1.2, # 기존 3.0 -> 1.2
            atk=25, rng=80, atk_spd=2.0,
            image_path=config.IMG_M2_2,
            attack_image_path=config.IMG_M2_2_A
        )

class MBoss(EnemyUnit):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=3000, 
            speed=0.4, # 기존 1.0 -> 0.4 (매우 느림)
            atk=100, rng=200, atk_spd=2.5,
            image_path=config.IMG_MBOSS,
            attack_image_path=config.IMG_MBOSS_A
        )