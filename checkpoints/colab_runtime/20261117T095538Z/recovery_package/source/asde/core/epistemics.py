from enum import StrEnum

class EpistemicStatus(StrEnum):
    CANDIDATE = "candidate"
    SUPPORTED = "supported"
    INDEPENDENTLY_REPLICATED = "independently_replicated"
    DISCONFIRMED = "disconfirmed"
    UNRESOLVED = "unresolved"
