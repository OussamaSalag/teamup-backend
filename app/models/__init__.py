# Re-export all models so Alembic autogenerate can detect every table.

from app.models.user import User, UserRole, Skill, ProfileSkill, UserPreference  # noqa: F401
from app.models.project import Project, ProjectMember, ProjectSkill, ProjectJoinRequest  # noqa: F401
from app.models.task import Task  # noqa: F401
from app.models.message import Conversation, ConversationParticipant, Message  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.mentor import MentorFeedback  # noqa: F401

__all__ = [
    "User",
    "UserRole",
    "Skill",
    "ProfileSkill",
    "UserPreference",
    "Project",
    "ProjectMember",
    "ProjectSkill",
    "ProjectJoinRequest",
    "Task",
    "Conversation",
    "ConversationParticipant",
    "Message",
    "Notification",
    "MentorFeedback",
]
