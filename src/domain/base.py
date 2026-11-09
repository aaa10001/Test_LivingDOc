"""领域层基类：实体与仓储接口。

这是给 LivingDoc 演示"复杂结构"用的样例代码，刻意保留了真实项目里的写法：
抽象基类、泛型接口、字段注入、组合关系。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


class DomainError(Exception):
    """领域层异常基类。"""


class NotFound(DomainError):
    """实体不存在。"""


@dataclass
class Entity:
    """所有实体的公共字段。"""

    id: int
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class User(Entity):
    email: str = ""
    display_name: str = ""


@dataclass
class AdminUser(User):
    """管理员：在用户之上多一层权限。"""

    scopes: list[str] = field(default_factory=list)

    def can(self, scope: str) -> bool:
        return scope in self.scopes or "*" in self.scopes


class Repository(ABC):
    """仓储接口。继承它的实现类必须给出这六个方法。"""

    @abstractmethod
    def find(self, entity_id: int) -> Entity | None: ...

    @abstractmethod
    def save(self, entity: Entity) -> Entity: ...

    @abstractmethod
    def delete(self, entity_id: int) -> bool: ...


class UserRepository(Repository):
    """内存版用户仓储；真实项目里这里是 SQLAlchemy 实现。"""

    def __init__(self, cache: "TTLCache | None" = None) -> None:
        self._rows: dict[int, User] = {}
        self._next_id = 1
        self.cache = cache or TTLCache(ttl_seconds=60)

    def find(self, entity_id: int) -> User | None:
        if entity_id in self._rows:
            return self._rows[entity_id]
        return self.cache.get(f"user:{entity_id}")

    def save(self, entity: Entity) -> User:
        row = entity if isinstance(entity, User) else User(id=self._next_id)
        if not row.id:
            row.id = self._next_id
            self._next_id += 1
        self._rows[row.id] = row
        self.cache.set(f"user:{row.id}", row)
        return row

    def delete(self, entity_id: int) -> bool:
        exists = self._rows.pop(entity_id, None) is not None
        self.cache.invalidate(f"user:{entity_id}")
        return exists

    def by_email(self, email: str) -> list[User]:
        found: list[User] = []
        for row in self._rows.values():
            if row.email.lower() == email.lower():
                found.append(row)
        return found

    def count(self, only_active: bool = True) -> int:
        """统计用户数；默认只数启用中的。"""
        if not only_active:
            return len(self._rows)
        total = 0
        for row in self._rows.values():
            if getattr(row, "active", True):
                total += 1
        return total


class TTLCache:
    """极简 TTL 缓存，用来制造"组合"关系。"""

    def __init__(self, ttl_seconds: int = 30) -> None:
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, tuple[object, datetime]] = {}

    def get(self, key: str) -> User | None:
        entry = self._items.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if datetime.now() > expires_at:
            self.invalidate(key)
            return None
        return value  # type: ignore[return-value]

    def set(self, key: str, value: object) -> None:
        from datetime import timedelta

        self._items[key] = (value, datetime.now() + timedelta(seconds=self.ttl_seconds))

    def invalidate(self, key: str) -> None:
        self._items.pop(key, None)