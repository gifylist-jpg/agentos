from enum import Enum


class StrictEnum(str, Enum):
    @classmethod
    def normalize(cls, value):
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @classmethod
    def has_value(cls, value: str) -> bool:
        value = cls.normalize(value)
        return value in cls._value2member_map_

    @classmethod
    def validate(cls, value):
        if isinstance(value, cls):
            return value

        value = cls.normalize(value)

        if not cls.has_value(value):
            raise ValueError(
                f"[ENUM ERROR] {value} not in {cls.__name__}: {list(cls._value2member_map_.keys())}"
            )

        return cls(value)

    def __str__(self):
        return self.value


class Stage(StrictEnum):
    EARLY = "EARLY"
    MID = "MID"
    LATE = "LATE"


class SignalStatus(StrictEnum):
    INSUFFICIENT = "INSUFFICIENT"
    PARTIAL = "PARTIAL"
    MATURE = "MATURE"


class Strength(StrictEnum):
    STRONG = "STRONG"
    NORMAL = "NORMAL"
    WEAK = "WEAK"


class Confidence(StrictEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class NoiseLevel(StrictEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Suggestion(StrictEnum):
    WAIT_MORE_DATA = "WAIT_MORE_DATA"
    KEEP_OBSERVING = "KEEP_OBSERVING"
    KEEP = "KEEP"
    RETEST_SAME_ANGLE_NEW_HOOK = "RETEST_SAME_ANGLE_NEW_HOOK"
    RETEST_SAME_HOOK_NEW_CTA = "RETEST_SAME_HOOK_NEW_CTA"
    DISTRIBUTION_PROBLEM = "DISTRIBUTION_PROBLEM"
    DROP_CURRENT_VARIANT = "DROP_CURRENT_VARIANT"
    AMPLIFY_CANDIDATE = "AMPLIFY_CANDIDATE"
    ARCHIVE_NO_SIGNAL = "ARCHIVE_NO_SIGNAL"
    FREEZE = "FREEZE"
