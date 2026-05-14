from enum import Enum


class UserRole(str, Enum):
    SUPER_ROOT = "super_root"
    ADMIN = "admin"
    USER = "user"


class TrustLevel(int, Enum):
    GUEST = 0  # 0未登录，只能浏览帖子
    BASIC = 1  # 1可以发帖评论，点赞关注收藏，资料，举报
    VERIFIED = 2  # 2可以隐藏学校，可以申请副版主
    CONTRIBUTOR = 3  # 3可以申请版主，可以申请新建模块


class SpaceType(str, Enum):
    COURSE = "course"
    SCHOOL = "school"
    INTEREST = "interest"


class PostType(str, Enum):
    DISCUSSION = "discussion"
    QUESTION = "question"
    RESOURCE = "resource"
    GUIDE = "guide"
    EXPERIENCE = "experience"
    NOTICE = "notice"
    POLL = "poll"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PENDING_REVIEW = "pending_review"
    HIDDEN = "hidden"
    LOCKED = "locked"
    DELETED = "deleted"


class SchoolVisibility(str, Enum):
    PUBLIC = "public"
    MEMBERS_ONLY = "members_only"
    HIDDEN = "hidden"
