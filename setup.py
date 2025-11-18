"""
ClaudeCode-Cola py2app 打包配置
"""
from setuptools import setup

APP = ['src/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/icons/app_icon.icns',  # 应用图标
    'plist': {
        'CFBundleName': 'ClaudeCode-Cola',
        'CFBundleDisplayName': 'ClaudeCode-Cola',
        'CFBundleGetInfoString': "Monitor Claude Code sessions and TodoWrite tasks",
        'CFBundleIdentifier': 'com.haya.claudecode-cola',
        'CFBundleVersion': '1.0.1',
        'CFBundleShortVersionString': '1.0.1',
        'NSHumanReadableCopyright': 'Copyright © 2024 Haya. All rights reserved.',
        'LSMinimumSystemVersion': '10.14.0',
        'LSUIElement': False,  # 显示在Dock中
        'NSHighResolutionCapable': True,
    },
    'packages': [
        'PyQt6',
        'watchdog',
        'psutil',
    ],
    'includes': [
        'src.app',
        'src.ui.main_window',
        'src.ui.system_tray',
        'src.ui.tray_popup',
        'src.core.session_monitor',
        'src.data.config',
        'src.data.models',
        'src.utils.logger',
        'src.utils.constants',
    ],
    'excludes': [
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
    ],
}

setup(
    name='ClaudeCode-Cola',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
