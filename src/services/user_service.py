"""服务层：组合、继承、异步、重试分支都在这里。

时序图的入口是 `UserService.load`：它调用仓储、调用缓存、在失败时重试，
正好覆盖"调用链 + 返回箭头 + alt/loop"三件事。
"""

from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable

from ..domain.base import AdminUser, NotFound, Repository, TTLCache, User, UserRepository

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3


class ServiceError(Exception):
    """服务层异常。"""


class BaseService:
    """所有服务的公共部分：统一的失败重试。"""

    def __init__(self, retries: int = _MAX_RETRIES) -> None:
        self.retries = retries

    def retry(self, action: Callable[[], object], attempts: int = 0) -> object:
        """同步重试：抛出异常就再来一次，次数用尽后原样抛出。"""
        last: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                return action()
            except ServiceError as exc:
                last = exc
                logger.warning("attempt %s failed: %s", attempt, exc)
        raise last if last else ServiceError("retry exhausted")


class AuditLog:
    """最小的审计日志：写一行、读最近几行。

    存内存而不是文件，示例项目不需要真的落盘；这样 `record`/`recent`
    的 if/for 分支足够短，类图上也不必为 I/O 细节留注解。
    """

    def __init__(self, capacity: int = 100) -> None:
        self.capacity = capacity
        self._lines: list[str] = []

    def record(self, event: str, user_id: int) -> None:
        """记录一条事件；超过容量时丢掉最早的一条。"""
        self._lines.append(f"{event}:{user_id}")
        while len(self._lines) > self.capacity:
            self._lines.pop(0)

    def recent(self, limit: int = 10) -> list[str]:
        """取最近 limit 条，倒序。"""
        if limit <= 0:
            return []
        return list(reversed(self._lines[-limit:]))


class UserService(BaseService):
    """用户服务：仓储 + 缓存 + 权限校验 + 审计。"""

    def __init__(
        self,
        repo: UserRepository,
        cache: TTLCache | None = None,
        audit: AuditLog | None = None,
    ) -> None:
        super().__init__(retries=2)
        self.repo = repo
        self.cache = cache or TTLCache(ttl_seconds=30)
        self.audit = audit or AuditLog()

    def load(self, user_id: int) -> User:
        """按 id 读用户，缓存优先，未命中回源，仍没有就抛 NotFound。"""
        cached = self.cache.get(f"user:{user_id}")
        if cached is not None:
            return cached
        user = self.repo.find(user_id)
        if user is None:
            raise NotFound(f"user {user_id} not found")
        self.cache.set(f"user:{user_id}", user)
        return user

    def register(self, email: str, display_name: str = "") -> User:
        """注册新用户；邮箱已存在时返回老用户，避免重复建号。"""
        for existing in self.repo.by_email(email):
            if existing.email == email:
                return existing
        user = self.repo.save(User(id=0, email=email, display_name=display_name or email))
        self.cache.set(f"user:{user.id}", user)
        return user

    def promote(self, user_id: int, scopes: list[str]) -> AdminUser:
        """把普通用户提升为管理员。"""
        user = self.load(user_id)
        admin = AdminUser(id=user.id, email=user.email, display_name=user.display_name, scopes=scopes)
        self.repo.save(admin)
        return admin

    def require(self, user: User, scope: str) -> None:
        """权限检查：只有管理员能过。"""
        if not isinstance(user, AdminUser):
            raise ServiceError(f"{user.email} is not an admin")
        if not user.can(scope):
            raise ServiceError(f"missing scope {scope}")

    def stats(self) -> dict[str, int]:
        """当前用户总数与最近审计条数，给运维面板用。"""
        active = self.repo.count()
        total = self.repo.count(only_active=False)
        recent = len(self.audit.recent(limit=5))
        if active < 0:
            raise ServiceError("negative active count")
        return {"active": active, "total": total, "recent": recent}

    def deactivate(self, user_id: int) -> bool:
        """停用用户：清缓存、改状态、写回仓储。

        返回 False 表示本来就是停用状态，调用方不需要重复通知。
        """
        user = self.load(user_id)
        if getattr(user, "active", True) is False:
            return False
        user.active = False
        self.repo.save(user)
        self.cache.invalidate(f"user:{user_id}")
        self.audit.record("deactivate", user_id)
        for watcher in getattr(self, "watchers", []):
            watcher.notify(user_id)
        return True


class SyncService(BaseService):
    """异步同步服务：带退避重试的批量拉取。"""

    def __init__(self, repo: Repository, fetch: Callable[[int], Awaitable[User | None]]) -> None:
        super().__init__(retries=3)
        self.repo = repo
        self.fetch = fetch

    async def sync(self, ids: list[int]) -> int:
        """逐个拉取远端用户并落库，返回成功条数。"""
        done = 0
        for user_id in ids:
            try:
                remote = await self.fetch(user_id)
                if remote is None:
                    logger.info("skip missing user %s", user_id)
                    continue
                self.repo.save(remote)
                done += 1
            except TimeoutError:
                await asyncio.sleep(0.1)
                continue
        return done

    async def sync_with_retry(self, ids: list[int]) -> dict[str, int]:
        """失败重试版：整体失败就退避重来，最多 retries 次。"""
        stats = {"ok": 0, "failed": 0}
        for attempt in range(self.retries + 1):
            try:
                stats["ok"] = await self.sync(ids)
                return stats
            except ServiceError:
                stats["failed"] += 1
                if attempt >= self.retries:
                    raise
                await asyncio.sleep(2**attempt)
        return stats