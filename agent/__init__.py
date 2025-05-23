"""
Agent package - Main functionality for your agent system.
"""
from .user_logger import UserLogger,setup_logger
from .lynis_audit import scanLynis
from .lynis import Lynis
from .rule import Rule,SystemRules

# Puoi definire qui cosa verrà esposto quando qualcuno importa il package
__version__ = '0.1.0'

# Opzionale: puoi importare e rendere disponibili direttamente le classi/funzioni principali
# from .core import Agent
# from .utils import helper_function
