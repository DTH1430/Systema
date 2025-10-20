# -*- mode: python ; coding: utf-8 -*-

# SystemScanner - Anti-Virus False Positive Mitigation
# This spec file includes version info and manifest to reduce AV false positives

import os
import reportlab
rl_path = os.path.dirname(reportlab.__file__)

a = Analysis(
    ['check.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('pdf_reporter.py', '.'),  # Include PDF reporter module
        (os.path.join(rl_path, 'fonts'), 'reportlab/fonts'),  # Include ReportLab fonts
    ],
    hiddenimports=[
        'pdf_reporter',
        # ReportLab and dependencies
        'reportlab',
        'reportlab.lib',
        'reportlab.lib.colors',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.platypus',
        'reportlab.platypus.doctemplate',
        'reportlab.platypus.paragraph',
        'reportlab.platypus.tables',
        'reportlab.graphics',
        'reportlab.graphics.shapes',
        'reportlab.graphics.charts',
        'reportlab.graphics.charts.piecharts',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        # PIL/Pillow
        'PIL',
        'PIL.Image',
        # Other necessary imports
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude unnecessary modules to reduce file size
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
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
    name='SystemScanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX disabled - reduces AV false positives
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Changed to True - shows console for transparency, less suspicious
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path here if you have one: 'scanner.ico'
    version='version_info.txt',  # Version information - IMPORTANT for AV trust
    uac_admin=True,  # Request admin explicitly in manifest
    uac_uiaccess=False,
    manifest='app.manifest',  # Application manifest for UAC
)
