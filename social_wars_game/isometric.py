"""
social_wars_game - İzometrik Matematik ve Koordinat Dönüşümleri (Isometric Engine)

Bu modül, 2D Kartezyen ızgara (x, y) ile 2.5D İzometrik Ekran (screen_x, screen_y)
arasındaki tüm matematiksel dönüşümleri yönetir.

Matematiksel Prensip:
Klasik izometrik oyunlarda (Social Wars, Age of Empires, SimCity 2000):
- X ekseni sağa ve aşağı doğru 30° eğimle uzanır.
- Y ekseni sola ve aşağı doğru 30° eğimle uzanır.
- Z ekseni (varsa) dik olarak yukarıya bakar.
"""

from settings import TILE_WIDTH, TILE_HEIGHT


def grid_to_screen(gx: float, gy: float, cam_x: float, cam_y: float) -> tuple[int, int]:
    """
    Izgara (gx, gy) koordinatını ekrandaki piksel (sx, sy) koordinatına çevirir.
    
    Formül:
      screen_x = (gx - gy) * (TILE_WIDTH / 2) + cam_x
      screen_y = (gx + gy) * (TILE_HEIGHT / 2) + cam_y
    """
    sx = int((gx - gy) * (TILE_WIDTH // 2) + cam_x)
    sy = int((gx + gy) * (TILE_HEIGHT // 2) + cam_y)
    return sx, sy


def screen_to_grid(sx: float, sy: float, cam_x: float, cam_y: float) -> tuple[int, int]:
    """
    Ekrandaki fare piksel koordinatını (sx, sy) ızgara koordinatına (gx, gy) çevirir.
    
    Formül:
      Ters matris çözümü ile:
      x' = sx - cam_x
      y' = sy - cam_y
      gx = (x' / (TILE_WIDTH / 2) + y' / (TILE_HEIGHT / 2)) / 2
      gy = (y' / (TILE_HEIGHT / 2) - x' / (TILE_WIDTH / 2)) / 2
    """
    adj_x = sx - cam_x
    adj_y = sy - cam_y

    half_w = TILE_WIDTH / 2.0
    half_h = TILE_HEIGHT / 2.0

    gx = (adj_x / half_w + adj_y / half_h) / 2.0
    gy = (adj_y / half_h - adj_x / half_w) / 2.0

    # int() yerine floor mantığı için tam sayıya yuvarlama:
    return int(gx if gx >= 0 else gx - 1), int(gy if gy >= 0 else gy - 1)


def get_tile_polygon(gx: int, gy: int, cam_x: float, cam_y: float) -> list[tuple[int, int]]:
    """
    Verilen (gx, gy) hücresi için izometrik elmasın (rhombus) 4 köşe noktasını döndürür:
    [Üst, Sağ, Alt, Sol]
    """
    center_x, center_y = grid_to_screen(gx, gy, cam_x, cam_y)
    half_w = TILE_WIDTH // 2
    half_h = TILE_HEIGHT // 2

    return [
        (center_x, center_y),                     # Üst köşe (Top)
        (center_x + half_w, center_y + half_h),   # Sağ köşe (Right)
        (center_x, center_y + TILE_HEIGHT),       # Alt köşe (Bottom)
        (center_x - half_w, center_y + half_h)    # Sol köşe (Left)
    ]
