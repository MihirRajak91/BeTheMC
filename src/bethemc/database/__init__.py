"""
Database module for BeTheMC MongoDB integration.
"""
from .connection import get_database
# The simple database layer does not define ODM document classes; export only what exists.
# Keep these imports guarded or remove them if documents are not implemented.
# from .models import PlayerDocument, GameStateDocument, SaveDocument
from .service import SimpleDatabaseService, get_database_service

__all__ = [
    "get_database",
    "SimpleDatabaseService",
    "get_database_service",
]