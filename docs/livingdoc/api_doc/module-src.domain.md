## src.domain

### AdminUser.can

- 签名：`def can(self, scope: str) -> bool`
- 说明：判断当前管理员是否具备指定权限范围：只要 `scope` 存在于 `self.scopes` 中，或 `self.scopes` 含有通配符 `"*"`，即视为具备该权限。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| scope | str | 是 | 待检查的权限范围字符串 |

- 返回值：返回 `bool`，`True` 表示具备该权限范围，`False` 表示不具备。
- 异常：无

### Repository.delete

- 签名：`def delete(self, entity_id: int) -> bool`
- 说明：抽象方法，用于按标识删除实体；具体实现由子类提供，代码中以 `@abstractmethod` 与 `...` 声明。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| entity_id | int | 是 | 待删除实体的标识 |

- 返回值：返回 `bool`，表示删除是否成功；具体判定逻辑代码中未体现。
- 异常：无

### Repository.find

- 签名：`def find(self, entity_id: int) -> Entity | None`
- 说明：抽象方法，用于按标识查找实体；具体实现由子类提供，代码中以 `@abstractmethod` 与 `...` 声明。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| entity_id | int | 是 | 待查找实体的标识 |

- 返回值：返回 `Entity | None`，找到时返回实体，未找到时返回 `None`；具体查找逻辑代码中未体现。
- 异常：无

### Repository.save

- 签名：`def save(self, entity: Entity) -> Entity`
- 说明：抽象方法，用于持久化实体；具体实现由子类提供，代码中以 `@abstractmethod` 与 `...` 声明。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| entity | Entity | 是 | 待保存的实体对象 |

- 返回值：返回 `Entity`，即保存后的实体；具体返回内容代码中未体现。
- 异常：无

### TTLCache.__init__

- 签名：`def __init__(self, ttl_seconds: int = 30) -> None`
- 说明：初始化带过期时间的缓存，记录 `ttl_seconds` 并创建内部字典 `_items`，其值由缓存对象与过期时间组成。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| ttl_seconds | int | 否 | 缓存条目的存活秒数，默认值为 `30` |

- 返回值：无返回值
- 异常：无

### TTLCache.get

- 签名：`def get(self, key: str) -> User | None`
- 说明：按键读取缓存；若条目不存在或已超过 `expires_at`，则调用 `invalidate` 清除该键并返回 `None`。代码中以 `# type: ignore[return-value]` 返回内部存储的 `object` 值。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| key | str | 是 | 缓存键 |

- 返回值：返回 `User | None`，命中且未过期时返回缓存值，否则返回 `None`。
- 异常：无

### TTLCache.invalidate

- 签名：`def invalidate(self, key: str) -> None`
- 说明：从内部字典 `_items` 中移除指定键，键不存在时不会报错（`pop` 传入默认值 `None`）。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| key | str | 是 | 待失效的缓存键 |

- 返回值：无返回值
- 异常：无

### TTLCache.set

- 签名：`def set(self, key: str, value: object) -> None`
- 说明：写入缓存条目，过期时间由 `datetime.now()` 加上 `ttl_seconds` 计算得到；`timedelta` 在函数内部延迟导入。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| key | str | 是 | 缓存键 |
| value | object | 是 | 待缓存的值 |

- 返回值：无返回值
- 异常：无

### UserRepository.__init__

- 签名：`def __init__(self, cache: "TTLCache | None" = None) -> None`
- 说明：初始化用户仓储，创建内部行字典 `_rows`、将 `_next_id` 置为 `1`，并在未传入 `cache` 时新建 `TTLCache(ttl_seconds=60)`。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| cache | TTLCache \| None | 否 | 可选的缓存实例，默认值为 `None`，为 `None` 时创建 TTL 为 60 秒的 `TTLCache` |

- 返回值：无返回值
- 异常：无

### UserRepository.by_email

- 签名：`def by_email(self, email: str) -> list[User]`
- 说明：遍历 `_rows` 中的所有用户，使用 `email.lower()` 做大小写不敏感比较，收集匹配的用户。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| email | str | 是 | 待匹配的邮箱地址，比较时忽略大小写 |

- 返回值：返回 `list[User]`，包含所有邮箱匹配的用户；无匹配时返回空列表。
- 异常：无

### UserRepository.delete

- 签名：`def delete(self, entity_id: int) -> bool`
- 说明：从 `_rows` 中弹出指定用户以判断是否存在，并无论是否存在都调用 `invalidate` 清除键 `user:{entity_id}` 的缓存。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| entity_id | int | 是 | 待删除用户的标识 |

- 返回值：返回 `bool`，`True` 表示 `_rows` 中原本存在该用户并被删除，`False` 表示原本不存在。
- 异常：无

### UserRepository.find

- 签名：`def find(self, entity_id: int) -> User | None`
- 说明：优先从 `_rows` 中查找；未命中时回退到缓存，读取键 `user:{entity_id}`。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| entity_id | int | 是 | 待查找用户的标识 |

- 返回值：返回 `User | None`，找到时返回用户对象，否则返回 `None`。
- 异常：无

### UserRepository.save

- 签名：`def save(self, entity: Entity) -> User`
- 说明：若 `entity` 是 `User` 实例则直接使用，否则以当前 `_next_id` 构造新的 `User`；当 `row.id` 为空时分配 `_next_id` 并自增，随后写入 `_rows` 并调用 `set` 缓存键 `user:{row.id}`。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| entity | Entity | 是 | 待保存的实体；为 `User` 实例时按其内容保存 |

- 返回值：返回 `User`，即写入 `_rows` 与缓存后的用户对象。
- 异常：无
