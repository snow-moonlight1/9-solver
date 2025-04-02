from dataclasses import dataclass
from typing import Optional, Set, Dict, List, Tuple
import math
import time
import random
import re
import sys
import select
import wave
import pyaudio
import io
import base64
import threading
from decimal import Decimal, getcontext
sys.stdout.reconfigure(encoding='utf-8')
getcontext().prec = 50

@dataclass
class Expression:
    """表达式类，存储数值和对应的字符串表示"""
    value: Decimal
    expr: str
    operators_used: set
    operator: Optional[str] = None
    priority: int = 0

    def __lt__(self, other):
        return self.priority < other.priority

    def __hash__(self):
        return hash(self.value)


class ImprovedNineExpressionFinder:
    def __init__(self):
        self._disable_divisions = False
        self.base_numbers = {Decimal('9'), Decimal('99'), Decimal('999')}
        from audio_data import AUDIO_DATA
        self.AUDIO_DATA = AUDIO_DATA
        self.large_number_threshold = 5000  # 大数阈值
        from expression_cache import EXPRESSION_CACHE
        self.expression_cache = EXPRESSION_CACHE
        self.max_line_length = 60  # 调整行长度
        # 将缓存中的表达式转换为符号形式
        self.expression_cache = {k: v.replace('9', '⑨ ') for k, v in self.expression_cache.items()}
        
    def play_baka_sound(self):
        thread = threading.Thread(target=self._play_audio, daemon=True)
        thread.start()

    def _play_audio(self):
        try:
            # 解码 base64 音频数据
            audio_binary = base64.b64decode(self.AUDIO_DATA)

            # 创建内存中的 wave 文件对象
            audio_file = io.BytesIO(audio_binary)
            wave_file = wave.open(audio_file, 'rb')

            # 设置 PyAudio
            p = pyaudio.PyAudio()

            # 打开音频流
            stream = p.open(format=p.get_format_from_width(wave_file.getsampwidth()),
                            channels=wave_file.getnchannels(),
                            rate=wave_file.getframerate(),
                            output=True)

            # 读取数据
            data = wave_file.readframes(1024)

            # 播放
            while data:
                stream.write(data)
                data = wave_file.readframes(1024)

            # 清理
            stream.stop_stream()
            stream.close()
            p.terminate()
            wave_file.close()

        except Exception as e:
            print(f"音频播放失败: {e}")

    def _get_operators(self, target: int) -> list:
        """根据目标值动态生成运算符优先级列表"""
        # 可选：对特殊数字定制规则
        if target % 10 == 0:
            return ['*', '/', '+', '-']

        if target > 1000:
            # 大目标优先乘法和加法
            return ['*', '+', '-', '/']
        elif target > 100:
            # 中等目标平衡运算
            return ['*', '+', '/', '-']
        else:
            # 小目标优先加减法
            return ['+', '-', '*', '/']

    def _is_operator(self, char: str) -> bool:
        return char in {'+', '-', '*', '/'}

    def _get_operator_precedence(self, op: str) -> int:
        if op in {'+', '-'}:
            return 1
        if op in {'*', '/'}:
            return 2
        return 0

    def _simplify_expression(self, expr: str) -> str:
        return expr.replace('+-', '-').replace('-+', '-')

    def _is_integer(self, num: float) -> bool:
        return abs(num - round(num)) < 1e-10

    def _estimate_distance(self, value: float, target: int) -> float:
        return abs(value - target)

    def _diversity_score(self, operators_used: set) -> float:
        score = len(operators_used) * 2
        if '*' in operators_used:
            score += 3
        return score

    def _is_worth_exploring(self, value: float, target: int, visited: Set[float]) -> bool:
        # 根据目标值动态调整允许的最大值
        factor = 100 if abs(target) > 1000 else 10
        max_allowed = max(abs(target) * factor, 10 ** 7)  # 调整倍数和基准值
        if abs(value) > max_allowed:
            return False
        if math.isinf(value) or math.isnan(value):
            return False
        if len(visited) > 100000:
            return False
        return True

    def _format_operand(self, exp: Expression, parent_op: str, is_right_operand: bool = False) -> str:
        if exp.operator is None:
            return exp.expr

        current_precedence = self._get_operator_precedence(exp.operator)
        parent_precedence = self._get_operator_precedence(parent_op)
        need_parenthesis = False

        if parent_op in {'+', '*'}:
            if current_precedence < parent_precedence:
                need_parenthesis = True
            elif current_precedence == parent_precedence and exp.operator != parent_op:
                need_parenthesis = True
        elif parent_op in {'-', '/'}:
            if is_right_operand:
                if current_precedence < parent_precedence:
                    need_parenthesis = True
                elif current_precedence == parent_precedence and exp.operator != parent_op:
                    need_parenthesis = True
            else:
                if current_precedence < parent_precedence:
                    need_parenthesis = True
                elif current_precedence == parent_precedence and exp.operator != parent_op:
                    need_parenthesis = True

        return f"({exp.expr})" if need_parenthesis else exp.expr

    def _evaluate(self, exp1: Expression, exp2: Expression, operator: str) -> Optional[Expression]:
        try:
            if operator == '+':
                value = exp1.value + exp2.value
            elif operator == '-':
                value = exp1.value - exp2.value
            elif operator == '*':
                value = exp1.value * exp2.value
            elif operator == '/':
                if abs(exp2.value) < 1e-10 or not self._is_integer(exp1.value / exp2.value):
                    return None
                value = exp1.value / exp2.value
            else:
                return None

            if abs(value) > 1e6:
                return None

            exp1_str = self._format_operand(exp1, operator)
            exp2_str = self._format_operand(exp2, operator, is_right_operand=True)
            expr = f"{exp1_str}{operator}{exp2_str}"
            expr = self._simplify_expression(expr)

            new_operators_used = exp1.operators_used | exp2.operators_used | {operator}
            return Expression(value, expr, new_operators_used, operator=operator)
        except:
            return None

    def _decompose_large_number(self, target: int) -> Optional[str]:
        """根据数字大小动态选择分解策略"""
        # 负数处理分支
        if target < 0:
            positive_expr = self._decompose_large_number(-target)
            if positive_expr:
                return f"-({positive_expr})"
            return None

        # 对于较小的数字，尝试使用更简单的组合
        if target < 1000:
            # 尝试用99和9的组合
            for base in [99, 9]:
                quotient = target // base
                remainder = target % base
                if quotient > 0:
                    # 对于较大的商，继续尝试分解
                    if quotient > 100:
                        quotient_expr = self._decompose_large_number(quotient)
                    else:
                        quotient_expr = self._find_expression_with_timeout(quotient, timeout_ms=300)
                    if quotient_expr:
                        if remainder == 0:
                            return f"{base}*({quotient_expr})"
                        remainder_expr = self._find_expression_with_timeout(remainder, timeout_ms=300)
                        if remainder_expr:
                            return f"{base}*({quotient_expr})+({remainder_expr})"
            return None

        # 对于中等大小的数字，优先尝试99和9的组合
        if target < self.large_number_threshold:
            # 先尝试99
            quotient = target // 99
            remainder = target % 99
            if quotient > 0:
                # 对于较大的商，继续尝试分解
                if quotient > 100:
                    quotient_expr = self._decompose_large_number(quotient)
                else:
                    quotient_expr = self._find_expression_with_timeout(quotient, timeout_ms=300)
                if quotient_expr:
                    if remainder == 0:
                        return f"99*({quotient_expr})"
                    remainder_expr = self._find_expression_with_timeout(remainder, timeout_ms=300)
                    if remainder_expr:
                        return f"99*({quotient_expr})+({remainder_expr})"
            
            # 再尝试9
            quotient = target // 9
            remainder = target % 9
            if quotient > 0:
                # 对于较大的商，继续尝试分解
                if quotient > 100:
                    quotient_expr = self._decompose_large_number(quotient)
                else:
                    quotient_expr = self._find_expression_with_timeout(quotient, timeout_ms=300)
                if quotient_expr:
                    if remainder == 0:
                        return f"9*({quotient_expr})"
                    remainder_expr = self._find_expression_with_timeout(remainder, timeout_ms=300)
                    if remainder_expr:
                        return f"9*({quotient_expr})+({remainder_expr})"

        # 对于大数，优先使用999
        quotient = target // 999
        remainder = target % 999
        if quotient > 0:
            # 对于较大的商，继续尝试分解
            if quotient > 100:
                quotient_expr = self._decompose_large_number(quotient)
            else:
                quotient_expr = self._find_expression_with_timeout(quotient, timeout_ms=300)
            if quotient_expr:
                if remainder == 0:
                    return f"999*({quotient_expr})"
                remainder_expr = self._find_expression_with_timeout(remainder, timeout_ms=300)
                if remainder_expr:
                    return f"999*({quotient_expr})+({remainder_expr})"
        
        # 如果所有尝试都失败，返回None
        return None

    def _find_expression_with_timeout(self, target: int, timeout_ms: int = 1000) -> Optional[str]:
        # 对于大数绝对值直接使用分解策略
        if abs(target) > 5000:
            return self._decompose_large_number(target)
        # 首先尝试启发式搜索
        # 数学约束预判
        self._disable_divisions = False
        if target % 9 != 0:  # 不能被9整除时禁用除以9的操作
            self._disable_divisions = True
        start_time = time.time()

        if target in self.expression_cache:
            return self.expression_cache[target]

        queue: List[Tuple[float, Expression]] = []
        visited: Set[float] = set()

        for num in self.base_numbers:
            expr_str = str(num).replace('9', '⑨ ')  # 替换基础数字为符号
            exp = Expression(float(num), str(num), set(), None)
            queue.append((self._estimate_distance(exp.value, target), exp))
            visited.add(exp.value)

        while queue and (time.time() - start_time) * 1000 < timeout_ms:
            import heapq
            # 使用堆结构优化优先级队列
            heapq.heapify(queue)
            current_priority, current_exp = heapq.heappop(queue)

            if self._is_integer(current_exp.value) and round(current_exp.value) == target:
                result = self._simplify_expression(current_exp.expr)
                self.expression_cache[target] = result
                return result

            # 动态获取运算符列表
            operators = self._get_operators(target)
            # 保留随机性但保持优先级
            random.shuffle(operators)
            # 将高优先级运算符移到前面
            for op in ['*', '+']:
                if op in operators:
                    operators.remove(op)
                    operators.insert(0, op)

            for base_num in self.base_numbers:
                base_exp = Expression(float(base_num), str(base_num), set(), None)

                for op in operators:
                    result = self._evaluate(current_exp, base_exp, op)
                    if result and result.value not in visited and self._is_worth_exploring(result.value, target,
                                                                                           visited):
                        queue.append((self._estimate_distance(result.value, target), result))
                        visited.add(result.value)

                    if op in {'-', '/'}:
                        reverse_result = self._evaluate(base_exp, current_exp, op)
                        if reverse_result and reverse_result.value not in visited and self._is_worth_exploring(
                                reverse_result.value, target, visited):
                            queue.append((self._estimate_distance(reverse_result.value, target), reverse_result))
                            visited.add(reverse_result.value)

        # 如果启发式搜索失败，尝试大数分解
        large_number_expr = self._decompose_large_number(target)
        if large_number_expr:
            return large_number_expr
            
        return None

    def _find_best_split_pos(self, tokens: list) -> int:
        for i in reversed(range(len(tokens))):
            if tokens[i] in {'*', '/'}:
                return i
        for i in reversed(range(len(tokens))):
            if tokens[i] in {'+', '-'}:
                return i
        return -1

    def _split_line(self, current_line: list, lines: list):
        if current_line:
            lines.append(''.join(current_line))
            current_line.clear()

    def _wrap_expression(self, expr: str) -> str:
        """优化后的自动换行方法"""
        if len(expr) <= self.max_line_length:
            return expr

        # 改进的正则表达式，正确识别所有运算符和数字
        tokens = re.findall(r'(\d+|\(|\)|\+|\-|\*|\/|\⑨\s*)', expr)
        tokens = [t for t in tokens if t.strip()]
        lines = []
        current_line = []
        current_length = 0

        for i, token in enumerate(tokens):
            token = token.strip()
            new_length = current_length + len(token) + (1 if current_line else 0)

            # 长数字预判换行，同时考虑运算符
            if (len(token) > 4 or token in {'*', '/'}) and current_length > self.max_line_length // 2:
                if current_line:
                    split_pos = self._find_best_split_pos(current_line)
                    if split_pos != -1:
                        head = current_line[:split_pos + 1]
                        tail = current_line[split_pos + 1:]
                        lines.append(''.join(head))
                        current_line = tail
                        current_length = sum(len(t) for t in tail)
                    else:
                        self._split_line(current_line, lines)
                        current_length = 0

            if new_length > self.max_line_length:
                split_pos = self._find_best_split_pos(current_line)
                if split_pos != -1:
                    head = current_line[:split_pos + 1]
                    tail = current_line[split_pos + 1:]
                    lines.append(''.join(head))
                    current_line = tail
                    current_length = sum(len(t) for t in tail)
                else:
                    self._split_line(current_line, lines)
                    current_length = 0

            current_line.append(token)
            current_length += len(token) + (1 if current_line else 0)

        if current_line:
            self._split_line(current_line, lines)

        # 优化换行后的格式
        if not lines:
            return expr

        wrapped = lines[0]
        for line in lines[1:]:
            # 确保运算符在行首时正确对齐
            if line[0] in {'+', '-', '*', '/'}:
                wrapped += '\n    ' + line
            else:
                wrapped += '\n    ' + line.lstrip()
        return wrapped

    def find_expression(self, target: int) -> str:
        result = self._find_expression_with_timeout(target)
        if result:
            # 如果原始表达式存在，转换为符号形式
            symbol_result = result.replace('9', '⑨ ')
            return symbol_result
            return ""


def main():
    finder = ImprovedNineExpressionFinder()
    print("\n欢迎使用⑨ 表达式求解器！")
    print("输入 'q' 退出程序。")

    while True:
        user_input = input("\n请输入目标整数: ").strip()
        if user_input.lower() in ['q', 'quit']:
            print("\033[38;2;1;101;204mbaka~\033[0m")
            finder.play_baka_sound()
            break

        try:
            # 支持科学计数法输入
            if 'e' in user_input.lower():
                target = int(float(user_input))
            else:
                target = int(user_input)
            start = time.time()
            expr = finder.find_expression(target)
            if expr:
                print(f"\n结果 ({time.time() - start:.2f}s):")
                print(f"{target} = {expr}")
                # 使用 ANSI 转义码设置文字颜色为 #0165cc（RGB: 1,101,204），打印 "baka~"
                print("\033[38;2;1;101;204mbaka~\033[0m")
                finder.play_baka_sound()
            else:
                # 如果搜索中断或找不到结果，原样输出提示信息
                print(expr)
        except ValueError:
            print("请输入有效整数或科学计数法(如1e3)！")

if __name__ == "__main__":
    main()
