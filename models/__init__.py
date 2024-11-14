"""
GhostSec Models Package
This package contains all database models for the GhostSec application.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import jwt
from time import time
from typing import Optional

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import all models to make them available when importing the package
from .user import User, followers
from .forum import ForumCategory, ForumPost, ForumComment
from .project import Project, ProjectMember
from .chat import ChatRoom, ChatMessage, ChatMember
from .lab import LabInstance, Report
from .achievement import Achievement

# Make all models available at package level
__all__ = [
    'db',
    'User',
    'followers',
    'ForumCategory',
    'ForumPost',
    'ForumComment',
    'Project',
    'ProjectMember',
    'ChatRoom',
    'ChatMessage',
    'ChatMember',
    'LabInstance',
    'Report',
    'Achievement',
]
