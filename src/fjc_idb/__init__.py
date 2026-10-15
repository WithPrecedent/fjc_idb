"""Makes using the FJC Integrated Database easier"""

from __future__ import annotations

from .downloader import create_folders, download, list_files
from .main import run

__version__ = '0.0.2'

__author__: str = 'Corey Rayburn Yung'

__all__: list[str] = ['create_folders', 'download', 'list_files', 'run']
