"""
social_wars_game - Varlık ve Nesne Modeli (Entities)

Bu modül oyundaki tüm nesneleri (Binalar, Ağaçlar, Taşlar, Birimler) tanımlar.
RaiseTheEmpires / Social Wars tarzında her nesnenin bir ızgara boyutu (size_x, size_y)
ve konumu (grid_x, grid_y) vardır.
"""

import pygame
from isometric import grid_to_screen, get_tile_polygon
from settings import (
    TILE_WIDTH, TILE_HEIGHT,
    COLOR_OBSTACLE_ROCK, COLOR_OBSTACLE_TREE, COLOR_BUILDING
)


class GameObject:
    """Tüm oyun varlıklarının (Binalar, Engeller, Birimler) temel sınıfı."""
    def __init__(self, obj_id: int, name: str, grid_x: int, grid_y: int, size_x: int = 1, size_y: int = 1):
        self.id = obj_id
        self.name = name
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.size_x = size_x
        self.size_y = size_y
        self.max_hp = 100
        self.hp = 100
        self.selected = False

    def occupies(self, gx: int, gy: int) -> bool:
        """Verilen hücre bu nesnenin sınırları içinde mi kontrol eder."""
        return (self.grid_x <= gx < self.grid_x + self.size_x and
                self.grid_y <= gy < self.grid_y + self.size_y)

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        """Nesneyi izometrik 3D blok olarak çizer."""
        pass


class Obstacle(GameObject):
    """Haritadaki doğal engeller: Ağaçlar, Kayalar, Çalılar."""
    def __init__(self, obj_id: int, name: str, grid_x: int, grid_y: int):
        super().__init__(obj_id, name, grid_x, grid_y, size_x=1, size_y=1)
        self.is_tree = "tree" in name.lower() or "bush" in name.lower() or "plant" in name.lower()
        self.color = COLOR_OBSTACLE_TREE if self.is_tree else COLOR_OBSTACLE_ROCK
        self.height_px = 30 if self.is_tree else 16

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        sx, sy = grid_to_screen(self.grid_x, self.grid_y, cam_x, cam_y)
        
        # Taban elması
        poly = get_tile_polygon(self.grid_x, self.grid_y, cam_x, cam_y)
        pygame.draw.polygon(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2), poly)
        
        # 3D Yükselti (Ağaç gövdesi / Kaya bloğu)
        top_y = sy - self.height_px
        if self.is_tree:
            # Ağaç çizimi (Tepe elips ve gövde)
            pygame.draw.line(surface, (90, 60, 30), (sx, sy + 15), (sx, top_y + 10), 4)
            pygame.draw.circle(surface, (35, 120, 50), (sx, top_y), 14)
            pygame.draw.circle(surface, (50, 160, 70), (sx, top_y - 4), 10)
        else:
            # Kaya çizimi (Prizmatik blok)
            rock_points = [
                (sx, top_y),
                (sx + 16, top_y + 8),
                (sx, top_y + 16),
                (sx - 16, top_y + 8)
            ]
            pygame.draw.polygon(surface, self.color, rock_points)
            pygame.draw.polygon(surface, (200, 200, 200), rock_points, 1)


class Building(GameObject):
    """Oyuncunun veya düşmanın binaları (Kışla, Fabrika, Ev vb.)"""
    def __init__(self, obj_id: int, name: str, grid_x: int, grid_y: int, size_x: int = 2, size_y: int = 2):
        super().__init__(obj_id, name, grid_x, grid_y, size_x, size_y)
        self.max_hp = 500
        self.hp = 500
        self.building_height = 40  # Yükseklik derinliği (px)
        self.color = COLOR_BUILDING

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        # Binanın kapladığı alanın tüm tabanını çiz
        # Binanın merkez ekran koordinatı
        base_sx, base_sy = grid_to_screen(self.grid_x, self.grid_y, cam_x, cam_y)
        
        # 2x2 veya 3x3 binanın köşe noktaları
        p_top = grid_to_screen(self.grid_x, self.grid_y, cam_x, cam_y)
        p_right = grid_to_screen(self.grid_x + self.size_x, self.grid_y, cam_x, cam_y)
        p_bottom = grid_to_screen(self.grid_x + self.size_x, self.grid_y + self.size_y, cam_x, cam_y)
        p_left = grid_to_screen(self.grid_x, self.grid_y + self.size_y, cam_x, cam_y)
        
        # Çatı noktaları (Yükseklik kadar yukarı ötelenmiş)
        h = self.building_height
        roof_top = (p_top[0], p_top[1] - h)
        roof_right = (p_right[0], p_right[1] - h)
        roof_bottom = (p_bottom[0], p_bottom[1] - h)
        roof_left = (p_left[0], p_left[1] - h)

        # 1. Sol duvar (Karanlık taraf)
        left_wall = [p_left, p_bottom, roof_bottom, roof_left]
        pygame.draw.polygon(surface, (40, 70, 120), left_wall)
        pygame.draw.polygon(surface, (20, 35, 60), left_wall, 1)

        # 2. Sağ duvar (Aydınlık taraf)
        right_wall = [p_bottom, p_right, roof_right, roof_bottom]
        pygame.draw.polygon(surface, (50, 90, 150), right_wall)
        pygame.draw.polygon(surface, (20, 35, 60), right_wall, 1)

        # 3. Çatı (Tavan elması)
        roof = [roof_top, roof_right, roof_bottom, roof_left]
        roof_color = (70, 125, 205) if not self.selected else (240, 200, 50)
        pygame.draw.polygon(surface, roof_color, roof)
        pygame.draw.polygon(surface, (255, 255, 255), roof, 2 if self.selected else 1)

        # Seçiliyse can çubuğu ve bina ismi
        if self.selected:
            bar_w = 60
            bar_h = 6
            bar_x = roof_top[0] - bar_w // 2
            bar_y = roof_top[1] - 15
            # Arka plan
            pygame.draw.rect(surface, (150, 0, 0), (bar_x, bar_y, bar_w, bar_h))
            # Yeşil can
            hp_w = int(bar_w * (self.hp / self.max_hp))
            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, hp_w, bar_h))
