@startuml
title UserRepository.find 时序图（模块 src/domain，文件 src/domain/base.py）

actor 调用方
participant UserRepository as repo
participant TTLCache as cache

调用方 -> repo : find(entity_id: int)
activate repo

repo -> cache : get(entity_id)
activate cache
alt 缓存命中且未过期
  cache --> repo : User
else 缓存未命中或已过期
  cache -> cache : invalidate(key)
  cache --> cache : 无返回值
  cache --> repo : None
end
deactivate cache

alt get 返回 User
  repo --> 调用方 : User
else get 返回 None
  repo --> 调用方 : None
end
deactivate repo

note over repo, cache
  输入未给出 UserRepository.find 的函数体，if 分支的实际条件依据 TTLCache.get 的返回值推断；
  类级结构关系（非本次调用链）：UserRepository --|> Repository，UserRepository *-- TTLCache，
  AdminUser --|> User，UserRepository ..> Entity，TTLCache ..> User；
  本次新增的 UserRepository.count 不在 find 的调用链上，故未展开。
end note
@enduml
