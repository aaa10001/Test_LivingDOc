@startuml
title UserService.deactivate 时序图（模块 src.services）

actor 调用方
participant UserService as svc
participant repo
participant cache

调用方 -> svc : deactivate(user_id: int)
activate svc
svc -> svc : load(user_id)
svc --> svc : user
alt getattr(user, "active", True) is False
  svc --> 调用方 : False（本来就是停用状态）
else 用户仍为启用状态
  svc -> svc : user.active = False
  svc -> repo : save(user)
  activate repo
  repo --> svc : 无返回值
  deactivate repo
  svc -> cache : invalidate(f"user:{user_id}")
  activate cache
  cache --> svc : 无返回值
  deactivate cache
  loop 遍历 getattr(self, "watchers", []) 中的每个 watcher
    svc -> svc : watcher.notify(user_id)
  end
  svc --> 调用方 : True
end
deactivate svc
note over svc
  UserService 继承 BaseService（源码基类），时序图无法表达泛化关系，故以此说明代替。
  repo、cache 与 watcher 的静态类型在输入中未给出，此处按字段名建模。
end note
@enduml
