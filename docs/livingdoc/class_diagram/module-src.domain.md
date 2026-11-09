@startuml
title src.domain 模块类图（src/domain/base.py）

abstract class Repository {
  +find(entity_id: int): Entity | None
  +save(entity: Entity): Entity
  +delete(entity_id: int): bool
}

class AdminUser {
  +scopes: list[str]
  +can(scope: str): bool
}

class TTLCache {
  +ttl_seconds
  +__init__(ttl_seconds: int = 30): None
  +get(key: str): User | None
  +set(key: str, value: object): None
  +invalidate(key: str): None
}

class UserRepository {
  -_next_id
  -cache: TTLCache
  +__init__(cache: TTLCache | None = None): None
  +find(entity_id: int): User | None
  +save(entity: Entity): User
  +delete(entity_id: int): bool
  +by_email(email: str): list[User]
  +count(only_active: bool = True): int
}

class User <<外部模块类型>>
class Entity <<外部模块类型>>
class True <<解析产物>>

AdminUser --|> User : 继承
UserRepository --|> Repository : 继承
UserRepository *-- TTLCache : 组合
Repository ..> Entity : 依赖
UserRepository ..> User : 依赖
UserRepository ..> Entity : 依赖
UserRepository ..> True : 依赖
TTLCache ..> User : 依赖

note right of UserRepository
  count 为本次新增方法：
  分支 if not only_active 直接返回总数；
  否则 for 遍历 _rows 并对每行 if 判断 active。
  find 调用 TTLCache.get，get 内部再触发 invalidate；
  save 调用 TTLCache.set，delete 调用 TTLCache.invalidate。
  by_email 含 for + if，find 含 if。
end note

legend right
  静态分析把 count 的默认值字面量 True
  误识别为类型，实际类型为 bool；
  此处按输入保留该依赖关系。
end legend
@enduml
