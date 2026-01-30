from typing import List


class ImporterError(Exception):
    """Custom exception raised by the importer when import validation fails."""

    def __init__(self, message: str, problems: List[str] = None) -> None:
        super().__init__(message)
        self.problems = problems or []
