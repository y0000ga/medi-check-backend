from enum import StrEnum


class PermissionLevel(StrEnum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class RelationshipStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"