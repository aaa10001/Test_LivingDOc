@startuml
title src.domain 模块类图

class User

abstract class Repository {
  +find(entity_id: int): Entity|None
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
  +get(key: str): User|None
  +set(key: str, value: object): None
  +invalidate(key: str): None
}

class UserRepository {
  -_next_id
  -cache
  +__init__(cache: TTLCache|None = None): None
  +find(entity_id: int): User|None
  +save(entity: Entity): User
  +delete(entity_id: int): bool
  +by_email(email: str): list[User]
}

AdminUser --|> User : 继承
UserRepository --|> Repository : 继承
UserRepository ..> TTLCache : 依赖

note right of UserRepository
  find：先查 _rows，未命中再调用 cache.get 回源；
  save：entity 不是 User 时新建 User 并自增 _next_id，
        写回 _rows 后调用 cache.set；
  delete：从 _rows 弹出并调用 cache.invalidate；
  by_email：遍历 _rows，按邮箱忽略大小写比较。
end note

note bottom of TTLCache
  get：条目不存在直接返回 None；
       过期则调用 invalidate 后返回 None；
  set：写入 (value, 过期时间) 二元组。
end note

note bottom of User
  User 与 Entity 为外部类型，本模块源码中未给出定义，
  此处仅作为继承与参数类型出现在关系中。
end note
@enduml
