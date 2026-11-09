@startuml
title 用户服务模块类图（src/services/user_service.py）

class AuditLog {
  -_lines: list[str]
  -capacity: int
  +__init__(capacity: int = 100) -> None
  +record(event: str, user_id: int) -> None
  +recent(limit: int = 10) -> list[str]
}

class BaseService {
  #retries: int
  +__init__(retries: int = _MAX_RETRIES) -> None
  +retry(action: Callable[[], object], attempts: int = 0) -> object
}

class SyncService {
  -repo: Repository
  -fetch: Callable[[int], Awaitable[User | None]]
  +__init__(repo: Repository, fetch: Callable[[int], Awaitable[User | None]])
  +async sync(ids: list[int]) -> int
  +async sync_with_retry(ids: list[int]) -> dict[str, int]
}

class UserService {
  -repo: UserRepository
  -cache: TTLCache
  -audit: AuditLog
  +__init__(repo: UserRepository, cache: TTLCache | None = None, audit: AuditLog | None = None)
  +load(user_id: int) -> User
  +register(email: str, display_name: str = "") -> User
  +promote(user_id: int, scopes: list[str]) -> AdminUser
  +require(user: User, scope: str) -> None
  +stats() -> dict[str, int]
  +deactivate(user_id: int) -> bool
}

class AdminUser
class Repository
class TTLCache
class User
class UserRepository

SyncService --|> BaseService : 继承
UserService --|> BaseService : 继承
SyncService *-- Repository : 组合
UserService *-- UserRepository : 组合
UserService *-- TTLCache : 组合
UserService *-- AuditLog : 组合
UserService ..> User : 依赖
UserService ..> AdminUser : 依赖
SyncService ..> User : 依赖

note right of UserService
  stats() 为本次新增方法：
  调用 repo.count() 两次（含 only_active=False），
  并用 audit.recent(limit=5) 统计最近审计条数；
  active 为负时抛出 ServiceError。
end note

note bottom of SyncService
  repo、fetch 字段类型在源码中为 Repository 与 Callable，
  依赖关系按 AST 抽取结果绘制。
end note
@enduml
