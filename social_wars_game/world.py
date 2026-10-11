"""
social_wars_game - Dünya ve Harita Yöneticisi (World & Map Loader)

Bu modül:
1. Izgara zeminini oluşturur ve çizer.
2. RaiseTheEmpires projesindeki gerçek `allies/initial-island.json` harita verilerini okur.
3. İzometrik derinlik sıralaması (Depth Sorting / Z-Order: x + y) yaparak nesneleri doğru katmanda çizer.
"""

import json
import os
import pygame
from isometric import get_tile_polygon, grid_to_screen
from entities import GameObject, Obstacle, Building
from settings import (
    MAP_WIDTH, MAP_HEIGHT,
    COLOR_GRASS_LIGHT, COLOR_GRASS_DARK, COLOR_GRID_LINE,
    COLOR_HIGHLIGHT
)


class World:
    def __init__(self, width: int = MAP_WIDTH, height: int = MAP_HEIGHT):
        self.width = width
        self.height = height
        self.objects: list[GameObject] = []
        self.selected_object: GameObject | None = None

    def add_object(self, obj: GameObject):
        """Dünyaya yeni bir nesne veya bina ekler."""
        self.objects.append(obj)

    def get_object_at(self, gx: int, gy: int) -> GameObject | None:
        """Belirtilen ızgara hücresinde bir nesne olup olmadığını bulur."""
        for obj in self.objects:
            if obj.occupies(gx, gy):
                return obj
        return None

    def load_from_island_json(self, json_path: str):
        """
        RaiseTheEmpires projesindeki island.json dosyasını (örn: allies/initial-island.json)
        ayrıştırarak dünyayı doldurur.
        """
        if not os.path.exists(json_path):
            print(f"Uyarı: Harita dosyası bulunamadı: {json_path}")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_objects = data.get("objects", [])
        print(f"Harita yükleniyor: {len(raw_objects)} nesne bulundu.")

        for item in raw_objects:
            obj_id = item.get("id", 0)
            item_name = item.get("itemName", "unknown")
            pos_str = item.get("position", "0,0,0")

            try:
                coords = [int(p) for p in pos_str.split(",")]
                gx, gy = coords[0], coords[1]
            except Exception:
                continue

            # Bina mı yoksa doğal engel mi?
            name_lower = item_name.lower()
            if any(b in name_lower for b in ["barracks", "hut", "bungalow", "hq", "building", "house"]):
                # Bina (2x2 boyut varsayımı)
                building = Building(obj_id, item_name, gx, gy, size_x=2, size_y=2)
                self.add_object(building)
            else:
                # Kaya, Ağaç, Çalı engelleri
                obstacle = Obstacle(obj_id, item_name, gx, gy)
                self.add_object(obstacle)

        print(f"Harita başarıyla yüklendi: {len(self.objects)} aktif varlık eklendi.")

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float, hover_gx: int, hover_gy: int):
        """
        1. Zemin karolarını çizer.
        2. Nesneleri derinlik sıralamasıyla (Z-Ordering) üst üste binmeyecek şekilde çizer.
        """
        screen_w, screen_h = surface.get_size()

        # 1. Zemin Karoları (Sadece ekranda görünenleri çizmek için basit sınır kontrolü)
        # 120x120 haritanın zeminini çiziyoruz
        for x in range(self.width):
            for y in range(self.height):
                # Ekran dışı optimizasyonu (Basit bounding box)
                sx, sy = grid_to_screen(x, y, cam_x, cam_y)
                if sx < -100 or sx > screen_w + 100 or sy < -100 or sy > screen_h + 100:
                    continue

                poly = get_tile_polygon(x, y, cam_x, cam_y)
                
                # Dama tahtası deseni (Çim çeşitliliği)
                tile_color = COLOR_GRASS_LIGHT if (x + y) % 2 == 0 else COLOR_GRASS_DARK
                pygame.draw.polygon(surface, tile_color, poly)
                pygame.draw.polygon(surface, COLOR_GRID_LINE, poly, 1)

        # Fare ile üzerine gelinen hücreyi vurgula
        if 0 <= hover_gx < self.width and 0 <= hover_gy < self.height:
            h_poly = get_tile_polygon(hover_gx, hover_gy, cam_x, cam_y)
            pygame.draw.polygon(surface, COLOR_HIGHLIGHT, h_poly, 2)

        # 2. İzometrik Derinlik Sıralaması (Depth Sorting)
        # İzometrikte arkadaki nesnelerin önce, öndeki nesnelerin sonra çizilmesi gerekir:
        # Sıralama anahtarı: (grid_x + grid_y)
        sorted_objects = sorted(self.objects, key=lambda obj: (obj.grid_x + obj.grid_y))

        for obj in sorted_objects:
            # Ekran dışı kontrolü
            sx, sy = grid_to_screen(obj.grid_x, obj.grid_y, cam_x, cam_y)
            if sx < -150 or sx > screen_w + 150 or sy < -150 or sy > screen_h + 150:
                continue

            obj.draw(surface, cam_x, cam_y)
