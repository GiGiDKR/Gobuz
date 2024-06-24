# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['gobuz/gobuz.py'],
    pathex=[],
    binaries=None,
    datas = [],
    hiddenimports=[],
    hookspath=None,
    hooksconfig={},
    runtime_hooks=None,
    excludes=None,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Gobuz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
	icon='gobuz/gobuz.ico'
)