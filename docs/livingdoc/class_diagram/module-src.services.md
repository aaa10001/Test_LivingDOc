@startuml
title UserService 类图（模块 src.services）

class BaseService

class UserService {
  -repo
  -cache
  +deactivate(user_id: int): bool
}

UserService --|> BaseService : 继承

note right of UserService
  deactivate 内部的控制流
  if 分支：getattr(user, "active", True) is False 时直接返回 False
  for 分支：遍历 getattr(self, "watchers", []) 并逐个调用 notify(user_id)
  方法内部还调用了 self.load(user_id) 与 self.repo.save(user)
end note
note bottom of UserService
  repo 与 cache 的具体类型未在输入中给出，因此未绘制依赖箭头
end note
@enduml
