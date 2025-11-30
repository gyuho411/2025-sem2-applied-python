import pygame
import config

# 기본 엔티티 클래스
class GameEntity(pygame.sprite.Sprite):
    """모든 캐릭터가 공유하는 기본 속성과 동작"""
    def __init__(self, x, y, hp, speed, attack_power, attack_range, attack_speed, team, image_name):
        super().__init__()
        # 기본 이미지 설정 (이미지 파일 없을 경우 대비 색상 박스)
        self.image_name = image_name
        self.image = pygame.Surface((50, 50))
        self.image.fill(config.BLUE if team == 'player' else config.RED)
        
        # 이미지 로드 시도
        self.load_image(f"images/{image_name}")
        
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        # 스탯 정의
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.attack_power = attack_power
        self.attack_range = attack_range
        
        # 공격 속도
        self.attack_cooldown = attack_speed * 1000 
        self.last_attack_time = 0
        
        self.team = team  # 'player' or 'enemy'
        self.state = "move"  # move, attack, idle

    def load_image(self, path):
        try:
            loaded_img = pygame.image.load(path)
            # 캐릭터 크기 통일
            if "Boss" in path:
                self.image = pygame.transform.scale(loaded_img, (150, 150)) # 보스는 크게
            else:
                self.image = pygame.transform.scale(loaded_img, (60, 60))
        except:
            pass

    def update(self, target_list, current_time):
        """매 프레임 실행: 행동 결정 (이동 vs 공격)"""
        if self.hp <= 0:
            self.kill()
            return

        target = self.find_nearest_target(target_list)

        if target:
            distance = abs(self.rect.centerx - target.rect.centerx)
            # 사거리 내에 적이 있으면 공격
            if distance <= self.attack_range:
                self.state = "attack"
                self.attack(target, current_time)
            else:
                self.state = "move"
                self.move()
        else:
            self.state = "move"
            self.move()

    def move(self):
        # 팀에 따라 이동 방향 결정 (플레이어: 오른쪽(+), 적: 왼쪽(-))
        direction = 1 if self.team == 'player' else -1
        self.rect.x += self.speed * direction

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

    def take_damage(self, amount):
        self.hp -= amount

# 팀별 중간 부모 클래스
class PlayerUnit(GameEntity):
    """아군 유닛 공통 정의"""
    def __init__(self, x, y, hp, speed, atk, rng, atk_spd, cost, spawn_delay, image_name):
        super().__init__(x, y, hp, speed, atk, rng, atk_spd, 'player', image_name)
        self.cost = cost              # 소환 비용 (돈)
        self.spawn_delay = spawn_delay # 재소환 쿨타임 (초)

class EnemyUnit(GameEntity):
    """적군 유닛 공통 정의"""
    def __init__(self, x, y, hp, speed, atk, rng, atk_spd, image_name):
        super().__init__(x, y, hp, speed, atk, rng, atk_spd, 'enemy', image_name)

# 개별 캐릭터 상세 정의 (스탯 설정)

# 아군
class C1(PlayerUnit):
    """기본 보병: 저렴하고 빠름"""
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=100, speed=3, atk=15, rng=50, atk_spd=0.8,
            cost=50, spawn_delay=1.0,
            image_name="C-1.png"
        )

class C2(PlayerUnit):
    """탱커: 체력이 높고 느림"""
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=400, speed=1, atk=10, rng=40, atk_spd=1.5,
            cost=200, spawn_delay=3.0,
            image_name="C-2.png"
        )

class C3(PlayerUnit):
    """원거리 딜러: 체력 낮음, 사거리 김, 공격력 높음"""
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=80, speed=2, atk=40, rng=250, atk_spd=2.0,
            cost=500, spawn_delay=5.0,
            image_name="C-3.png"
        )

# 적군

class M1_1(EnemyUnit):
    """잡몹 1: 약함"""
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=60, speed=2, atk=8, rng=40, atk_spd=1.0,
            image_name="M1-1.png"
        )

class M1_2(EnemyUnit):
    """잡몹 2: 조금 빠름"""
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=90, speed=4, atk=12, rng=40, atk_spd=0.8,
            image_name="M1-2.png"
        )

class M2_1(EnemyUnit):
    """중급 몹 1: 튼튼함"""
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=250, speed=1, atk=20, rng=50, atk_spd=1.5,
            image_name="M2-1.png"
        )

class M2_2(EnemyUnit):
    """중급 몹 2: 원거리 공격"""
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=150, speed=2, atk=25, rng=200, atk_spd=2.0,
            image_name="M2-2.png"
        )

class MBoss(EnemyUnit):
    """최종 보스: 매우 강력함"""
    def __init__(self, x, y):
        super().__init__(
            x, y,
            hp=3000, speed=1, atk=100, rng=100, atk_spd=2.5,
            image_name="M-Boss.png"
        )