from enum import Enum


class SyslogFormat(Enum):
    """Enumeration of supported syslog message formats"""
    RFC5424 = "rfc5424"
    RFC3164 = "rfc3164"
    LEGACY = "legacy"
    NO_PRI = "no_pri"
    CISCO = "cisco"
    UNKNOWN = "unknown"
