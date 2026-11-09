## src.services

### UserService.deactivate

- 签名：`def deactivate(self, user_id: int) -> bool:`
- 说明：停用指定用户，流程为先用 `self.load(user_id)` 加载用户，若 `user.active` 为 `False` 则直接返回，否则把 `active` 置为 `False` 并调用 `self.repo.save(user)` 写回仓储。随后调用 `self.cache.invalidate(f"user:{user_id}")` 清除缓存，并遍历 `self.watchers` 逐个调用 `watcher.notify(user_id)`。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `user_id` | `int` | 是 | 要停用的用户标识，用于 `self.load(user_id)` 加载用户以及构造缓存键 `f"user:{user_id}"` |

- 返回值：返回 `bool`。返回 `True` 表示本次调用完成了状态修改、仓储写回、缓存清除与观察者通知；返回 `False` 表示用户本来就是停用状态，此时不会重复通知调用方，代码在该分支直接返回。
- 异常：无。
