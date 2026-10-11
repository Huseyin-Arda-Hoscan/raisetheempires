import sys
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

TMP_BUNDLED_DIR = sys._MEIPASS if getattr(sys, 'frozen', None) else APP_DIR
ASSETS_DIR = os.path.join(TMP_BUNDLED_DIR, 'assets')
STUB_DIR = os.path.join(TMP_BUNDLED_DIR, 'stub')
TEMPLATES_DIR = os.path.join(TMP_BUNDLED_DIR, 'templates')
VILLAGES_DIR = os.path.join(TMP_BUNDLED_DIR, 'villages')
QUESTS_DIR = os.path.join(VILLAGES_DIR, 'quest')
CONFIG_DIR = os.path.join(TMP_BUNDLED_DIR, 'config')
CONFIG_PATCH_DIR = os.path.join(CONFIG_DIR, 'patch')
BASE_DIR = APP_DIR
MODS_DIR = os.path.join(BASE_DIR, 'mods')
SAVES_DIR = os.path.join(BASE_DIR, 'saves')
AUCTIONS_DIR = os.path.join(BASE_DIR, 'auctions')
