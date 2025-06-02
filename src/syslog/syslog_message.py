import ipaddress
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from syslog_formats import SyslogFormat


class SyslogMessage:
    """
    Represents a syslog message that can be parsed into its different
    components.

    Usage:
        msg = SyslogMessage("<13>Oct 11 22:14:15 hostname app[123]: message")
        print(f"Severity: {msg.severity}")
        print(f"Timestamp: {msg.datetime}")
        print(f"NetworkMessage: {msg.message}")
    """

    # Facility codes
    FACILITIES = {
        0: "kern", 1: "user", 2: "mail", 3: "daemon", 4: "auth", 5: "syslog",
        6: "lpr", 7: "news", 8: "uucp", 9: "cron", 10: "authpriv", 11: "ftp",
        12: "ntp", 13: "security", 14: "console", 15: "clock", 16: "local0",
        17: "local1", 18: "local2", 19: "local3", 20: "local4", 21: "local5",
        22: "local6", 23: "local7"
    }

    # Severity codes
    SEVERITIES = {
        0: "emergency", 1: "alert", 2: "critical", 3: "error",
        4: "warning", 5: "notice", 6: "info", 7: "debug"
    }

    # Regex patterns for different syslog formats
    PATTERNS = {
        SyslogFormat.RFC5424: re.compile(
            r'<(?P<pri>\d+)>(?P<version>\d+) (?P<timestamp>\d{4}-\d{2}-\d{'
            r'2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?) '
            r'(?P<hostname>[\w\-\.:%]+) '
            r'(?P<app_name>[^ \[\]]+) (?P<proc_id>[^ \[\]]+) (?P<msg_id>[^ \['
            r'\]]+) '
            r'(?P<structured_data>(?:\[[^\]]+\])+|-) '
            r'(?P<message>.*)'
        ),
        SyslogFormat.RFC3164: re.compile(
            r'<(?P<pri>\d+)>(?P<timestamp>[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{'
            r'2}:\d{2}) '
            r'(?P<hostname>[\w\-\.:%]+) '
            r'(?P<tag>[a-zA-Z0-9_/.-]+)(?:\[(?P<pid>\d+)\])?: '
            r'(?P<message>.*)'
        ),
        SyslogFormat.LEGACY: re.compile(
            r'<(?P<pri>\d+)>(?P<timestamp>[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{'
            r'2}:\d{2}) '
            r'(?P<hostname>[\w\-\.:%]+) '
            r'(?P<tag>[a-zA-Z0-9_/.-]+): '
            r'(?P<message>.*)'
        ),
        SyslogFormat.NO_PRI: re.compile(
            r'(?P<timestamp>[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}) '
            r'(?P<hostname>[\w\-\.:%]+) '
            r'(?P<tag>[a-zA-Z0-9_/.-]+)(?:\[(?P<pid>\d+)\])?: '
            r'(?P<message>.*)'
        ),
        SyslogFormat.CISCO: re.compile(
            r'<(?P<pri>\d+)>(?P<timestamp>[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{'
            r'2}:\d{2}(?:\.\d+)?'
            r'(?:\s+[A-Za-z]{3,4})?): %(?P<facility>[A-Z0-9]+)-('
            r'?P<severity>\d)-(?P<mnemonic>[A-Z0-9_]+): '
            r'(?P<message>.*)'
        )
    }

    # Pattern for structured data
    SD_PATTERN = re.compile(
        r'\[(?P<sd_id>[^@=\] ]+)(?:@(?P<pen>\d+))?(?: (?P<params>[^]]+))?\]')
    SD_PARAM_PATTERN = re.compile(
        r'(?P<param_name>[^=]+)="(?P<param_value>(?:[^"\\]|\\["\\])*)"')

    def __init__(self, raw_message: str, received_at: Optional[str] = None,
                 received_by: Optional[str] = None):
        """
        Initialize a new SyslogMessage by parsing the raw message string.

        Args:
            raw_message: The raw syslog message string
            received_at: Timestamp when message was received (YYYY-MM-DD
            HH:MM:SS)
            received_by: Identifier of the system that received this message
        """
        self.raw_message = raw_message
        self.received_at = received_at or datetime.utcnow().strftime(
            '%Y-%m-%d %H:%M:%S')
        self.received_by = received_by or "SyslogParser"

        # Initialize fields with default values
        self._format = SyslogFormat.UNKNOWN
        self._parsed_data = {}
        self._pri = None
        self._facility_code = None
        self._severity_code = None
        self._timestamp_str = None
        self._datetime = None
        self._hostname = None
        self._host_type = None
        self._app_name = None
        self._proc_id = None
        self._pid = None
        self._msg_id = None
        self._tag = None
        self._structured_data = None
        self._structured_data_parsed = None
        self._message = raw_message
        self._version = None
        self._cisco_facility = None
        self._cisco_severity = None
        self._cisco_mnemonic = None

        # Parse the message
        self._parse()

    def _parse(self):
        """Parse the raw message and populate the object's properties."""
        # Try each pattern in order of specificity
        for format_type, pattern in self.PATTERNS.items():
            match = pattern.match(self.raw_message)
            if match:
                self._format = format_type
                self._parsed_data = match.groupdict()

                # Extract fields based on format
                self._extract_fields()
                return

        # If no pattern matches
        self._format = SyslogFormat.UNKNOWN
        self._message = self.raw_message

    def _extract_fields(self):
        """Extract and process fields from the parsed data."""
        # Extract priority-related fields
        if "pri" in self._parsed_data:
            self._pri = int(self._parsed_data["pri"])
            self._facility_code = self._pri // 8
            self._severity_code = self._pri % 8

        # Extract timestamp
        if "timestamp" in self._parsed_data:
            self._timestamp_str = self._parsed_data["timestamp"]
            self._parse_timestamp()

        # Extract hostname and classify it
        if "hostname" in self._parsed_data:
            self._hostname = self._parsed_data["hostname"]
            self._host_type, _ = self._classify_hostname(self._hostname)

        # Extract message format-specific fields
        if self._format == SyslogFormat.RFC5424:
            self._version = self._parsed_data.get("version")
            self._app_name = self._parsed_data.get("app_name")
            self._proc_id = self._parsed_data.get("proc_id")
            self._msg_id = self._parsed_data.get("msg_id")

            # Parse structured data
            sd_string = self._parsed_data.get("structured_data")
            if sd_string and sd_string != "-":
                self._structured_data = sd_string
                self._structured_data_parsed = self._parse_structured_data(
                    sd_string)

        elif self._format in (
                SyslogFormat.RFC3164, SyslogFormat.LEGACY, SyslogFormat.NO_PRI):
            self._tag = self._parsed_data.get("tag")
            self._pid = self._parsed_data.get("pid")

        elif self._format == SyslogFormat.CISCO:
            self._cisco_facility = self._parsed_data.get("facility")
            self._cisco_severity = self._parsed_data.get("severity")
            self._cisco_mnemonic = self._parsed_data.get("mnemonic")

        # Extract the message content
        if "message" in self._parsed_data:
            self._message = self._parsed_data["message"]

    def _parse_timestamp(self):
        """Parse the timestamp string into a datetime object."""
        try:
            if self._format == SyslogFormat.RFC5424:
                # RFC5424 uses ISO8601 format
                ts = self._timestamp_str
                # Handle various RFC5424 timestamp formats
                if 'T' in ts:
                    if ts.endswith('Z'):
                        ts = ts[:-1] + '+00:00'
                    self._datetime = datetime.fromisoformat(ts)
                else:
                    # Some implementations may not use 'T' separator
                    self._datetime = datetime.fromisoformat(ts)
            else:
                # For BSD/legacy formats (assuming current year)
                current_year = datetime.now().year
                ts = f"{current_year} {self._timestamp_str}"
                self._datetime = datetime.strptime(ts, "%Y %b %d %H:%M:%S")
        except ValueError:
            # Keep the original timestamp string if parsing fails
            self._datetime = None

    def _parse_structured_data(self, sd_string: str) -> List[Dict[str, Any]]:
        """Parse RFC5424 structured data elements."""
        result = []
        for match in self.SD_PATTERN.finditer(sd_string):
            sd_element = {
                "sd_id": match.group("sd_id"),
                "enterprise_id": match.group("pen"),
                "parameters": {}
            }

            if match.group("params"):
                for param_match in self.SD_PARAM_PATTERN.finditer(
                        match.group("params")):
                    param_name = param_match.group("param_name")
                    param_value = param_match.group("param_value")
                    # Handle escaped characters in parameter values
                    param_value = param_value.replace('\\"', '"').replace(
                        '\\\\', '\\')
                    sd_element["parameters"][param_name] = param_value

            result.append(sd_element)

        return result

    def _classify_hostname(self, hostname: str) -> Tuple[str, str]:
        """Determine if hostname is an IP address (IPv4/IPv6) or name."""
        try:
            ipaddress.ip_address(hostname)
            return "ip", hostname
        except ValueError:
            return "name", hostname

    # Properties for accessing the parsed fields

    @property
    def format(self) -> SyslogFormat:
        """Get the detected format of the syslog message."""
        return self._format

    @property
    def format_name(self) -> str:
        """Get the format name as a string."""
        return self._format.value

    @property
    def is_valid(self) -> bool:
        """Check if the message was successfully parsed."""
        return self._format != SyslogFormat.UNKNOWN

    @property
    def pri(self) -> Optional[int]:
        """Get the priority value."""
        return self._pri

    @property
    def facility_code(self) -> Optional[int]:
        """Get the numeric facility code."""
        return self._facility_code

    @property
    def facility(self) -> Optional[str]:
        """Get the facility name."""
        if self._facility_code is None:
            return None
        return self.FACILITIES.get(self._facility_code,
                                   f"unknown({self._facility_code})")

    @property
    def severity_code(self) -> Optional[int]:
        """Get the numeric severity code."""
        return self._severity_code

    @property
    def severity(self) -> Optional[str]:
        """Get the severity name."""
        if self._severity_code is None:
            return None
        return self.SEVERITIES.get(self._severity_code,
                                   f"unknown({self._severity_code})")

    @property
    def timestamp(self) -> Optional[str]:
        """Get the original timestamp string."""
        return self._timestamp_str

    @property
    def datetime(self) -> Optional[datetime]:
        """Get the parsed timestamp as a datetime object."""
        return self._datetime

    @property
    def hostname(self) -> Optional[str]:
        """Get the hostname."""
        return self._hostname

    @property
    def host_type(self) -> Optional[str]:
        """Get the hostname type (ip or name)."""
        return self._host_type

    @property
    def app_name(self) -> Optional[str]:
        """Get the application name (RFC5424)."""
        return self._app_name

    @property
    def proc_id(self) -> Optional[str]:
        """Get the process ID (RFC5424)."""
        return self._proc_id

    @property
    def pid(self) -> Optional[str]:
        """Get the PID (RFC3164/Legacy)."""
        return self._pid

    @property
    def msg_id(self) -> Optional[str]:
        """Get the message ID (RFC5424)."""
        return self._msg_id

    @property
    def tag(self) -> Optional[str]:
        """Get the tag (RFC3164/Legacy)."""
        return self._tag

    @property
    def structured_data(self) -> Optional[str]:
        """Get the raw structured data string (RFC5424)."""
        return self._structured_data

    @property
    def structured_data_parsed(self) -> Optional[List[Dict[str, Any]]]:
        """Get the parsed structured data (RFC5424)."""
        return self._structured_data_parsed

    @property
    def message(self) -> str:
        """Get the message content."""
        return self._message

    @property
    def version(self) -> Optional[str]:
        """Get the version (RFC5424)."""
        return self._version

    @property
    def cisco_facility(self) -> Optional[str]:
        """Get the Cisco facility."""
        return self._cisco_facility

    @property
    def cisco_severity(self) -> Optional[str]:
        """Get the Cisco severity."""
        return self._cisco_severity

    @property
    def cisco_mnemonic(self) -> Optional[str]:
        """Get the Cisco mnemonic."""
        return self._cisco_mnemonic

    def to_dict(self) -> Dict[str, Any]:
        """Convert the parsed syslog message to a dictionary."""
        result = {
            "raw_message": self.raw_message,
            "format": self.format_name,
            "parsed": self.is_valid,
            "received_at": self.received_at,
            "received_by": self.received_by
        }

        # Add other fields if they exist
        if self.pri is not None:
            result["pri"] = self.pri
            result["facility_code"] = self.facility_code
            result["facility"] = self.facility
            result["severity_code"] = self.severity_code
            result["severity"] = self.severity

        if self.timestamp:
            result["timestamp"] = self.timestamp

        if self.datetime:
            result["datetime"] = self.datetime.isoformat()

        if self.hostname:
            result["hostname"] = self.hostname
            result["host_type"] = self.host_type

        # Add format-specific fields
        if self.format == SyslogFormat.RFC5424:
            result["version"] = self.version
            result["app_name"] = self.app_name
            result["proc_id"] = self.proc_id
            result["msg_id"] = self.msg_id

            if self.structured_data:
                result["structured_data"] = self.structured_data
                result["structured_data_parsed"] = self.structured_data_parsed

        elif self.format in (
                SyslogFormat.RFC3164, SyslogFormat.LEGACY, SyslogFormat.NO_PRI):
            result["tag"] = self.tag
            if self.pid:
                result["pid"] = self.pid

        elif self.format == SyslogFormat.CISCO:
            result["cisco_facility"] = self.cisco_facility
            result["cisco_severity"] = self.cisco_severity
            result["cisco_mnemonic"] = self.cisco_mnemonic

        result["message"] = self.message

        return result

    def to_db_row(self) -> Dict[str, Any]:
        """
        Prepare the message for database storage with flattened structured data.
        This is optimized for relational database storage.
        """
        # Start with the basic dictionary
        row = self.to_dict()

        # Convert datetime to string if it exists
        if "datetime" in row and isinstance(row["datetime"], datetime):
            row["datetime"] = row["datetime"].isoformat()

        # Remove complex nested structures that can't be directly stored in SQL
        if "structured_data_parsed" in row:
            del row["structured_data_parsed"]

        return row

    def get_structured_data_rows(self) -> List[Dict[str, Any]]:
        """
        Get structured data elements as separate rows for relational database
        storage.
        Returns a list of dictionaries representing SD elements.
        """
        if not self.structured_data_parsed:
            return []

        result = []
        for sd_element in self.structured_data_parsed:
            element_row = {
                "sd_id": sd_element["sd_id"],
                "enterprise_id": sd_element["enterprise_id"]
            }

            # Add parameters as flattened fields
            for param_name, param_value in sd_element.get("parameters",
                                                          {}).items():
                element_row[f"param_{param_name}"] = param_value

            result.append(element_row)

        return result

    def __str__(self) -> str:
        """String representation of the syslog message."""
        if not self.is_valid:
            return f"Invalid syslog message: {self.raw_message}"

        parts = [f"Format: {self.format_name}"]

        if self.pri is not None:
            parts.append(
                f"Priority: {self.pri} (Facility: {self.facility}, Severity: "
                f"{self.severity})")

        if self.datetime:
            parts.append(f"Timestamp: {self.datetime.isoformat()}")
        elif self.timestamp:
            parts.append(f"Timestamp: {self.timestamp}")

        if self.hostname:
            parts.append(f"Host: {self.hostname} ({self.host_type})")

        if self.format == SyslogFormat.RFC5424:
            parts.append(
                f"App: {self.app_name}, ProcID: {self.proc_id}, MsgID: "
                f"{self.msg_id}")

            if self.structured_data_parsed:
                sd_parts = []
                for sd in self.structured_data_parsed:
                    params = ", ".join([f"{k}={v}" for k, v in
                                        sd.get("parameters", {}).items()])
                    sd_parts.append(f"{sd['sd_id']}: {params}")
                parts.append(f"Structured Data: {'; '.join(sd_parts)}")

        elif self.format in (
                SyslogFormat.RFC3164, SyslogFormat.LEGACY, SyslogFormat.NO_PRI):
            parts.append(
                f"Tag: {self.tag}" + (f", PID: {self.pid}" if self.pid else ""))

        elif self.format == SyslogFormat.CISCO:
            parts.append(
                f"Cisco: {self.cisco_facility}-{self.cisco_severity}-"
                f"{self.cisco_mnemonic}")

        parts.append(f"NetworkMessage: {self.message}")

        return "\n".join(parts)
