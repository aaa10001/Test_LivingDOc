## src.domain

### UserRepository.count

- 签名：`def count(self, only_active: bool = True) -> int`
- 说明：统计用户数量，默认只统计处于启用状态（`active` 为真）的用户；当 `only_active` 为 `False` 时返回全部行数。
- 参数表：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `only_active` | `bool` | 否（默认 `True`） | 为 `True` 时只统计 `active` 属性为真的行；为 `False` 时直接返回 `self._rows` 的总长度。 |

- 返回值：返回 `int`，即满足条件的用户数量。
- 异常：无
