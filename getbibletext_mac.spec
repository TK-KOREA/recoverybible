# -*- mode: python ; coding: utf-8 -*-
# macOS용 빌드 spec — .app 번들 생성
# 빌드: pyinstaller --clean -y getbibletext_mac.spec

block_cipher = None

a = Analysis(
    ['getbibletext.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('recovery_bible_ko.xml', '.'),
        ('recovery_bible_en.xml', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='getbibletext',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='getbibletext',
)

app = BUNDLE(
    coll,
    name='회복역성경가져오기.app',
    icon='favicon.icns',
    bundle_identifier='com.tkkorea.recoverybible',
    version='1.0.0',
    info_plist={
        'CFBundleName': '회복역성경가져오기',
        'CFBundleDisplayName': '회복역성경가져오기',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
