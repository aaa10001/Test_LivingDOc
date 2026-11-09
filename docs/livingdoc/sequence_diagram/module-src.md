@startuml
title Calculator.add 调用序列（入口点：Calculator.add）

actor 调用方 as Caller
participant "Calculator" as Calc

note over Caller
  说明：输入中未给出调用方类型，
  此处以“调用方”表示，属于推断关系
end note

note over Calc
  本次变更的方法：
  __init__(self, history=None)
  add(self, a: float, b: float) -> float
  divide(self, a: float, b: float) -> float
end note

note over Calc
  本次新增函数：
  format_result(value: float) -> str
  （未被 add 调用，本入口点中无交互）
end note

Caller -> Calc : add(a: float, b: float)
activate Calc
Calc -> Calc : result = a + b
Calc -> Calc : self.history.append(("add", a, b, result))
Calc --> Caller : return result
deactivate Calc

note over Caller, Calc
  divide 中的 b == 0 分支会抛出 ZeroDivisionError，
  该分支不在本入口点 add 的调用路径上
end note
@enduml
