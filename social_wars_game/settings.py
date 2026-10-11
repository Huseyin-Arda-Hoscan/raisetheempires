"""
social_wars_game - Yapılandırma ve Sabitler (Settings)
"""

# Ekran Ayarları
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750
FPS = 60
TITLE = "Social Wars & Empires - 2.5D Isometric Python RTS"

# İzometrik Karo (Tile) Ayarları
# Standart 2:1 izometrik oran (Genişlik 64px, Yükseklik 32px)
TILE_WIDTH = 64
TILE_HEIGHT = 32

# Harita Ayarları
# Başlangıçta 100x100 ızgara alanı
MAP_WIDTH = 120
MAP_HEIGHT = 120

# Kamera Hızı
CAMERA_SPEED = 12

# Renk Paleti (RGB)
COLOR_BG = (18, 22, 28)              # Arka plan boşluk rengi
COLOR_GRASS_LIGHT = (56, 118, 64)    # Çimen açık yeşil
COLOR_GRASS_DARK = (48, 102, 54)     # Çimen koyu yeşil (dama deseni için)
COLOR_GRID_LINE = (38, 80, 42)       # Izgara çizgileri
COLOR_HIGHLIGHT = (255, 230, 80)     # Fareyle üzerine gelinen karo (Vurgu)
COLOR_HIGHLIGHT_FILL = (255, 255, 120, 60) # Yarı saydam seçim

# Nesne ve Bina Renkleri (Görsel asset'ler bağlanana kadar prototip bloklar)
COLOR_OBSTACLE_ROCK = (120, 120, 125)  # Kayalar
COLOR_OBSTACLE_TREE = (28, 82, 35)     # Ağaçlar
COLOR_BUILDING = (60, 100, 175)        # Binalar (Kışla / HQ)
COLOR_UI_PANEL = (25, 30, 40, 220)     # UI Arka planı
COLOR_TEXT = (240, 240, 245)           # Yazı rengi
COLOR_GOLD = (255, 204, 0)             # Altın sarısı
