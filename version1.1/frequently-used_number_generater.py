# generate_combinations.py
import itertools
from collections import defaultdict


class CombinationGenerator:
    def __init__(self):
        self.base = [9, 99, 999]
        self.operators = ['+', '-', '*', '/']
        self.combinations = defaultdict(list)
        self.special_values = {1000, 2000, 5000, 10000}
        self.priority_ops = ['*', '+', '-', '/']  # 新增运算符优先级实例变量

    def _precompute_special_values(self):
        """为特殊数值生成快速通道组合"""
        special_combinations = {
            1000: [('999+9', 1008), ('99*9', 891)],
            2000: [('999*2', 1998), ('99*20', 1980)],
            5000: [('999*5', 4995), ('99*50', 4950)],
            10000: [('999*10', 9990), ('99*101', 9999)]
        }

        # 调整运算符优先级顺序：乘法 > 加法 > 减法 > 除法
        
        for target, bases in special_combinations.items():
            for expr, base_val in bases:
                for op in self.priority_ops:
                    result = self._evaluate(base_val, 9, op)
                    if result and abs(result - target) < 50:
                        self.combinations[result].append(f'({expr}){op}9')

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
        # 预处理特殊数值
        self._precompute_special_values()
        
        # 单步运算组合（优化排列方式）
        perm_cache = set()
        for a, b in itertools.permutations(self.base, 2):
            if (a, b) not in perm_cache:
                perm_cache.add((a, b))
                for op in self.operators:
                    res = self._evaluate(a, b, op)
                    if res is not None and (abs(res) < 50_000 or res in self.special_values):
                        expr = f"{a}{op}{b}"
                        self.combinations[res].append(expr)

        # 两步运算组合（动态剪枝策略）
        temp = {k: v for k, v in self.combinations.items() if k < 10_000 or k in self.special_values}
        for val in sorted(temp.keys(), key=lambda x: -abs(x)):  # 按数值大小倒序处理
            for base in sorted(self.base, reverse=True):
                for op in self.priority_ops:  # 使用实例变量中的运算符优先级
                    res = self._evaluate(val, base, op)
                    if res and (abs(res) < 100_000 or res in self.special_values):
                        for expr in temp[val]:
                            new_expr = f"({expr}){op}{base}"
                            # 表达式复杂度控制（限制嵌套层数）
                            if new_expr.count('(') < 3:
                                self.combinations[res].append(new_expr)

        # 去重并保留最短表达式
        final = {}
        for k in self.combinations:
            if k == int(k):  # 只保留整数
                sorted_exprs = sorted(set(self.combinations[k]), key=len)
                final[int(k)] = sorted_exprs[0]
        return final


if __name__ == "__main__":
    try:
        gen = CombinationGenerator()
        combinations = gen.generate()
    except Exception as e:
        print("\n\033[91m错误详情：")
        print(f"异常类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"发生位置: {e.__traceback__.tb_lineno}行\033[0m")
        raise
    print("高频组合生成结果（前20个示例）：")
    for i, (k, v) in enumerate(list(combinations.items())[:20]):
        print(f"{k} = {v}")
    print("\n完整结果已生成，请复制以下字典到主程序：")
    print("{")
    for k, v in combinations.items():
        print(f"    {k}: '{v}',")
    print("}")