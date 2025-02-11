# generate_combinations.py
import itertools
from collections import defaultdict


class CombinationGenerator:
    def __init__(self):
        self.base = [9, 99, 999]
        self.operators = ['+', '-', '*', '/']
        self.combinations = defaultdict(list)

    def _evaluate(self, a, b, op):
        try:
            if op == '+': return a + b
            if op == '-': return a - b
            if op == '*': return a * b
            if op == '/':
                if b == 0 or a % b != 0:
                    return None
                return a // b
            return None
        except:
            return None

    def generate(self):
        # 单步运算组合
        for a, b in itertools.permutations(self.base, 2):
            for op in self.operators:
                res = self._evaluate(a, b, op)
                if res is not None and abs(res) < 100_000:
                    expr = f"{a}{op}{b}"
                    self.combinations[res].append(expr)

        # 两步运算组合
        temp = dict(self.combinations)
        for val in temp:
            for base in self.base:
                for op in self.operators:
                    res = self._evaluate(val, base, op)
                    if res is not None and abs(res) < 100_000:
                        for expr in temp[val]:
                            new_expr = f"({expr}){op}{base}"
                            self.combinations[res].append(new_expr)

        # 去重并保留最短表达式
        final = {}
        for k in self.combinations:
            if k == int(k):  # 只保留整数
                sorted_exprs = sorted(set(self.combinations[k]), key=len)
                final[int(k)] = sorted_exprs[0]
        return final


if __name__ == "__main__":
    gen = CombinationGenerator()
    combinations = gen.generate()
    print("高频组合生成结果（前20个示例）：")
    for i, (k, v) in enumerate(list(combinations.items())[:20]):
        print(f"{k} = {v}")
    print("\n完整结果已生成，请复制以下字典到主程序：")
    print("{")
    for k, v in combinations.items():
        print(f"    {k}: '{v}',")
    print("}")