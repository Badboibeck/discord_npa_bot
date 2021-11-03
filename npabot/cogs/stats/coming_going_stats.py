from collections import defaultdict
import datetime
from typing import Dict, Set, Optional, List, Tuple


class ComingGoingStats(object):
    _coming: int
    _going: int
    _reacted_coming: int
    _reacted_going: int
    _before: datetime.datetime
    _after: datetime.datetime
    _coming_reacted_names: Dict[str, int]
    _going_reacted_names: Dict[str, int]

    def __init__(self, before: datetime.datetime, after: datetime.datetime):
        self._coming = 0
        self._going = 0
        self._reacted_coming = 0
        self._reacted_going = 0
        self._before = before
        self._after = after
        self._coming_reacted_names = defaultdict(int)
        self._going_reacted_names = defaultdict(int)

    def add_coming(self, reacted: bool, names: Optional[Set[str]] = None):
        self._coming += 1
        if reacted:
            self._reacted_coming += 1
        if names is not None:
            for name in names:
                self._coming_reacted_names[name] += 1

    def add_going(self, reacted: bool, names: Optional[Set[str]] = None):
        self._going += 1
        if reacted:
            self._reacted_going += 1
        if names is not None:
            for name in names:
                self._going_reacted_names[name] += 1

    @property
    def coming(self) -> int:
        return self._coming

    @property
    def going(self) -> int:
        return self._going

    @property
    def reacted_coming(self) -> int:
        return self._reacted_coming

    @property
    def reacted_going(self) -> int:
        return self._reacted_going

    @property
    def before(self) -> datetime.datetime:
        return self._before

    @property
    def after(self) -> datetime.datetime:
        return self._after

    @property
    def coming_reacted_names(self) -> Dict[str, int]:
        return self._coming_reacted_names

    @property
    def going_reacted_names(self) -> Dict[str, int]:
        return self._going_reacted_names

    def get_reacted_coming_percentage(self) -> float:
        if self._coming == 0:
            return -1.0
        return (self._reacted_coming / self._coming) * 100

    def get_reacted_going_percentage(self) -> float:
        if self._going == 0:
            return -1.0
        return (self._reacted_going / self._going) * 100

    def sorted_coming_reacted_names(self) -> List[Tuple[str, int]]:
        return sorted(
            [(k, v) for k, v in self.coming_reacted_names.items()],
            key=lambda x: x[1],
            reverse=True,
        )

    def sorted_going_reacted_names(self) -> List[Tuple[str, int]]:
        return sorted(
            [(k, v) for k, v in self.going_reacted_names.items()],
            key=lambda x: x[1],
            reverse=True,
        )
