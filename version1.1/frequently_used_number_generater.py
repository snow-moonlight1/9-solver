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

    def _generate_base_combinations(self):
        """生成基础数字的组合"""
        for a in self.base:
            for b in self.base:
                for op in self.operators:
                    res = self._evaluate(a, b, op)
                    if res is not None and abs(res) < 50_000:
                        expr = f"{a}{op}{b}"
                        self.combinations[res].append(expr)
                        
                        # 尝试与第三个基础数进行组合
                        for c in self.base:
                            for op2 in self.operators:
                                final_res = self._evaluate(res, c, op2)
                                if final_res is not None and abs(final_res) < 100_000:
                                    final_expr = f"({expr}){op2}{c}"
                                    self.combinations[final_res].append(final_expr)

    def _evaluate(self, a, b, op):
        try:
            if op == '+': return a + b
            if op == '-': return a - b
            if op == '*': return a * b
            if op == '/':
                if b == 0:
                    return None
                return a / b
            return None
        except:
            return None

    def generate(self):
        # 生成基础组合
        self._generate_base_combinations()
        
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
    print("\n完整结果已生成，请复制以下字典到主程序：")
    print("{")
    for k, v in combinations.items():
        print(f"    {k}: '{v}',")
    print("}")