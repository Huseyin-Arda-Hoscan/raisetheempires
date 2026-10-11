"""
social_wars_game - Ana Giriş Noktası (Game Main Loop)

Çalıştırmak için:
  python social_wars_game/main.py
"""

import os
import sys
import pygame

# Kendi modüllerimizi içe aktarıyoruz
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    COLOR_BG, COLOR_UI_PANEL, COLOR_TEXT, COLOR_GOLD, CAMERA_SPEED
)
from isometric import screen_to_grid, grid_to_screen
from world import World
from entities import Building


def main():
    # 1. Pygame Başlatma
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Segoe UI", 16)
    font_bold = pygame.font.SysFont("Segoe UI", 18, bold=True)
    font_title = pygame.font.SysFont("Segoe UI", 22, bold=True)

    # 2. Dünya ve Harita Oluşturma
    world = World()
    
    # RaiseTheEmpires projesindeki gerçek ada dosyasının yolu:
    island_json_path = os.path.join(os.path.dirname(__file__), "..", "allies", "initial-island.json")
    island_json_path = os.path.normpath(island_json_path)

    if os.path.exists(island_json_path):
        world.load_from_island_json(island_json_path)
    else:
        print(f"Uyarı: {island_json_path} bulunamadı, boş harita açılıyor.")

    # 3. Başlangıç Kamera Konumu
    # `initial-island.json` içindeki binalar 70-85 koordinatları etrafında toplanmıştır.
    # Kamerayı başlangıçta bu binaların tam ortasına odaklayalım:
    target_gx, target_gy = 75, 80
    center_sx = (target_gx - target_gy) * 32
    center_sy = (target_gx + target_gy) * 16

    camera_x = SCREEN_WIDTH // 2 - center_sx
    camera_y = SCREEN_HEIGHT // 2 - center_sy

    # Kaynaklar (Social Wars tarzı ekonomi)
    resources = {
        "gold": 2500,
        "steel": 1200,
        "population": 15,
        "max_pop": 50,
        "level": 8
    }

    # Fareyle sürükleme (Mouse Dragging / Panning) durumları
    is_dragging = False
    drag_start_mouse = (0, 0)
    drag_start_cam = (0, 0)

    # İnşaat Modu (Build Mode)
    build_mode = False

    running = True
    while running:
        # A. Olay / Event Yönetimi
        mouse_pos = pygame.mouse.get_pos()
        hover_gx, hover_gy = screen_to_grid(mouse_pos[0], mouse_pos[1], camera_x, camera_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Fare Tıklamaları
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol Tık: Seçim yap veya Bina kur
                    if build_mode:
                        # Seçili hücreye yeni bina ekle
                        new_bldg = Building(
                            obj_id=len(world.objects) + 2000,
                            name="Oyuncu Kışlası",
                            grid_x=hover_gx,
                            grid_y=hover_gy,
                            size_x=2,
                            size_y=2
                        )
                        world.add_object(new_bldg)
                        resources["gold"] -= 150
                        build_mode = False
                        print(f"Bina kuruldu: ({hover_gx}, {hover_gy})")
                    else:
                        # Hücredeki nesneyi seç
                        target = world.get_object_at(hover_gx, hover_gy)
                        if world.selected_object:
                            world.selected_object.selected = False
                        world.selected_object = target
                        if target:
                            target.selected = True

                elif event.button == 3 or event.button == 2:  # Sağ Tık veya Orta Tık: Kamera Sürükleme Başlat
                    is_dragging = True
                    drag_start_mouse = mouse_pos
                    drag_start_cam = (camera_x, camera_y)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3 or event.button == 2:
                    is_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging:
                    dx = mouse_pos[0] - drag_start_mouse[0]
                    dy = mouse_pos[1] - drag_start_mouse[1]
                    camera_x = drag_start_cam[0] + dx
                    camera_y = drag_start_cam[1] + dy

            # Klavye Tuşları
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    # 'B' tuşuna basınca inşaat modunu aç/kapat
                    build_mode = not build_mode
                elif event.key == pygame.K_ESCAPE:
                    build_mode = False
                    if world.selected_object:
                        world.selected_object.selected = False
                        world.selected_object = None

        # B. Sürekli Klavye Girdisi ile Kamera Hareketi (W-A-S-D)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            camera_x += CAMERA_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            camera_x -= CAMERA_SPEED
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            camera_y += CAMERA_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            camera_y -= CAMERA_SPEED

        # C. Çizim (Rendering)
        screen.fill(COLOR_BG)

        # 1. İzometrik Dünyayı Çiz
        world.draw(screen, camera_x, camera_y, hover_gx, hover_gy)

        # 2. İnşaat Önizlemesi (Ghost Building)
        if build_mode:
            ghost = Building(0, "Yeni Bina", hover_gx, hover_gy, 2, 2)
            ghost.building_height = 30
            ghost.draw(screen, camera_x, camera_y)

        # 3. Üst Bilgi Barı (HUD / Economy Bar)
        hud_surface = pygame.Surface((SCREEN_WIDTH, 48), pygame.SRCALPHA)
        hud_surface.fill(COLOR_UI_PANEL)
        screen.blit(hud_surface, (0, 0))
        pygame.draw.line(screen, (60, 75, 100), (0, 48), (SCREEN_WIDTH, 48), 2)

        # HUD Metinleri
        hud_text = (
            f"👑 Seviye: {resources['level']}   |   "
            f"💰 Altın: {resources['gold']}   |   "
            f"⚙️ Çelik: {resources['steel']}   |   "
            f"👥 Nüfus: {resources['population']}/{resources['max_pop']}"
        )
        screen.blit(font_bold.render(hud_text, True, COLOR_GOLD), (20, 12))

        # Sağ üst yardım metni
        help_text = "[W-A-S-D / Fare Sağ Tık: Harita Gezinme]  [B: Bina İnşa Et]  [ESC: İptal]"
        screen.blit(font.render(help_text, True, (180, 200, 220)), (SCREEN_WIDTH - 540, 14))

        # 4. Sol Alt: Seçilen Nesne Paneli
        if world.selected_object:
            panel_w, panel_h = 300, 120
            panel_x, panel_y = 20, SCREEN_HEIGHT - panel_h - 20

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((20, 25, 35, 230))
            screen.blit(panel, (panel_x, panel_y))
            pygame.draw.rect(screen, (80, 120, 180), (panel_x, panel_y, panel_w, panel_h), 2)

            obj = world.selected_object
            screen.blit(font_title.render(f"{obj.name}", True, COLOR_TEXT), (panel_x + 15, panel_y + 10))
            screen.blit(font.render(f"Tür: {type(obj).__name__}", True, (170, 180, 200)), (panel_x + 15, panel_y + 40))
            screen.blit(font.render(f"Konum: ({obj.grid_x}, {obj.grid_y}) | Boyut: {obj.size_x}x{obj.size_y}", True, (170, 180, 200)), (panel_x + 15, panel_y + 65))
            screen.blit(font.render(f"Can: {obj.hp} / {obj.max_hp}", True, (100, 230, 120)), (panel_x + 15, panel_y + 90))

        # 5. İnşaat Modu Uyarısı
        if build_mode:
            banner = font_bold.render("İnşaat Modu Aktif: Kurmak istediğiniz yere tıklayın (Maliyet: 150 Altın)", True, (255, 220, 50))
            screen.blit(banner, (SCREEN_WIDTH // 2 - banner.get_width() // 2, 60))

        # 6. Kareyi Güncelle
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
