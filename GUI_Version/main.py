from dataclasses import dataclass
from typing import Optional, Set, List, Tuple
import math
import time
import random
import re
import wave
import pyaudio
import io
import base64
import threading
import gmpy2
from gmpy2 import mpz

@dataclass
class Expression:
    """表达式类，存储数值和对应的字符串表示"""
    value: mpz
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
        self.base_number_map = {
            mpz(9): '⑨',
            mpz(99): '⑨⑨',
            mpz(999): '⑨⑨⑨',
            mpz(3): '√⑨'
        }
        self.base_numbers = set(self.base_number_map.keys())
        from baka_sound import BAKA_DATA
        self.BAKA_DATA = BAKA_DATA
        self.large_number_threshold = 5000  # 大数阈值
        from expression_cache import EXPRESSION_CACHE
        self.expression_cache = EXPRESSION_CACHE
        self.max_line_length = 60  # 调整行长度
        # 将缓存中的表达式转换为符号形式
        self.expression_cache = {k: v.replace('9', '⑨') for k, v in self.expression_cache.items()}
        # 为新的分解算法预先计算好构造块
        self.greedy_blocks = self._precompute_greedy_blocks()

    def _precompute_greedy_blocks(self) -> List[Tuple[mpz, str]]:
        """预计算用于贪心分解的构造块，并按数值大小降序排列"""
        blocks = []
        
        # 基础数字
        n_9, n_99, n_999 = mpz(9), mpz(99), mpz(999)
        blocks.append((n_999, '⑨⑨⑨'))
        blocks.append((n_99, '⑨⑨'))
        blocks.append((n_9, '⑨'))
        
        # 平方
        blocks.append((n_999 * n_999, '⑨⑨⑨*⑨⑨⑨'))
        blocks.append((n_99 * n_99, '⑨⑨*⑨⑨'))
        blocks.append((n_9 * n_9, '⑨*⑨'))

        # 特殊的小数（用 mpz(3) 代表 √⑨）
        blocks.append((mpz(8), '⑨-⑨/⑨'))
        blocks.append((mpz(7), '⑨-√⑨+⑨/⑨'))
        blocks.append((mpz(6), '⑨-√⑨'))
        blocks.append((mpz(5), '⑨-√⑨-⑨/⑨'))
        blocks.append((mpz(4), '√⑨+⑨/⑨'))
        blocks.append((mpz(3), '√⑨'))
        blocks.append((mpz(2), '(⑨+⑨)/⑨'))
        blocks.append((mpz(1), '⑨/⑨'))
        
        # 按数值大小降序排序
        blocks.sort(key=lambda item: item[0], reverse=True)
        return blocks
    
    def play_baka_sound(self):
        thread = threading.Thread(target=self._play_audio, daemon=True)
        thread.start()

    def _play_audio(self):
        try:
            # 解码 base64 音频数据
            audio_binary = base64.b64decode(self.BAKA_DATA)

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

    def _is_worth_exploring(self, value: mpz, target: mpz, visited: Set[mpz]) -> bool:
        # 使用gmpy2，理论上没有上限，但为了防止状态空间爆炸，仍然可以设置一个阈值
        factor = 100
        max_allowed = abs(target) * factor if target != 0 else mpz(10**7)
        if abs(value) > max_allowed:
            return False
        
        # 状态空间限制
        if len(visited) > 100000: # 限制BFS的搜索广度
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
            value = mpz(0)
            if operator == '+':
                value = exp1.value + exp2.value
            elif operator == '-':
                value = exp1.value - exp2.value
            elif operator == '*':
                value = exp1.value * exp2.value
            elif operator == '/':
                if exp2.value == 0: return None
                # 使用gmpy2.is_divisible确保整除
                if not gmpy2.is_divisible(exp1.value, exp2.value):
                    return None
                value = exp1.value // exp2.value # 使用整数除法
            else:
                return None

            exp1_str = self._format_operand(exp1, operator)
            exp2_str = self._format_operand(exp2, operator, is_right_operand=True)
            expr = f"{exp1_str}{operator}{exp2_str}"
            expr = self._simplify_expression(expr)

            new_operators_used = exp1.operators_used | exp2.operators_used | {operator}
            return Expression(value, expr, new_operators_used, operator=operator)
        except:
            return None

    def _decompose_large_number(self, target: mpz) -> Optional[str]:
        """
        使用基于gmpy2的贪心算法快速分解大数。
        这个函数会递归调用，并返回一个部分表达式列表。
        """
        if target < 0:
            # 处理负数
            decomposed_positive = self._decompose_large_number_recursive_parts(-target)
            if decomposed_positive:
                return f"-({self._format_decomposed_parts(decomposed_positive)})"
            return None

        # 对于正数，直接调用并格式化
        parts = self._decompose_large_number_recursive_parts(target)
        if parts:
            return self._format_decomposed_parts(parts)
        return None

    def _decompose_large_number_recursive_parts(self, target: mpz) -> List[str]:
        """递归分解的核心，返回一个字符串列表，如 ['999*999', '+', '9*9']"""
        if target == 0:
            return []

        # 优先从预计算的构造块中查找
        for value, expr_str in self.greedy_blocks:
            if target == value:
                return [expr_str]
        
        # 贪心算法：尝试用最大的构造块去除
        for value, expr_str in self.greedy_blocks:
            if value <= target:
                # 尝试整除
                quotient, remainder = gmpy2.f_divmod(target, value)
                if quotient > 0:
                    # 分解商
                    quotient_parts = self._decompose_large_number_recursive_parts(quotient)
                    if not quotient_parts: # 如果商无法分解，此路不通
                        continue
                    
                    # 组合结果
                    result_parts = []
                    if len(quotient_parts) == 1 and quotient_parts[0] == '⑨/⑨': # 商为1，则省略 "1*"
                        result_parts.append(expr_str)
                    else:
                        result_parts.extend([expr_str, '*', f"({self._format_decomposed_parts(quotient_parts)})"])
                    
                    # 如果有余数，继续分解余数
                    if remainder > 0:
                        remainder_parts = self._decompose_large_number_recursive_parts(remainder)
                        if not remainder_parts: # 余数无法分解
                            continue
                        result_parts.append('+')
                        result_parts.extend(remainder_parts)
                    
                    return result_parts
        
        # 如果所有尝试都失败
        return []

    def _format_decomposed_parts(self, parts: List[str]) -> str:
        """将分解后的部分列表格式化为最终的字符串表达式。"""
        # 将部分连接起来，不加多余的空格
        return "".join(parts)

    def _find_expression_with_timeout(self, target_int: int, timeout_ms: int = 900) -> Optional[str]:
        target = mpz(target_int) # 将输入转换为gmpy2的mpz类型

        # 1. 检查缓存
        if target_int in self.expression_cache:
            return self.expression_cache[target_int]

        # 2. 对于较小的数，优先使用BFS/A*搜索
        if abs(target) < self.large_number_threshold:
            self._disable_divisions = (target % 9 != 0)
            start_time = time.time()
            
            # (这里的BFS逻辑基本不变，但需要确保它使用mpz类型)
            queue: List[Tuple[mpz, Expression]] = []
            visited: Set[mpz] = set()

            for num, expr_str in self.base_number_map.items():
                exp = Expression(num, expr_str, set(), None)
                # 估算距离时转为float，因为距离不需要绝对精度
                distance = abs(float(exp.value - target))
                queue.append((distance, exp))
                visited.add(exp.value)

            import heapq
            heapq.heapify(queue)

            while queue and (time.time() - start_time) * 1000 < timeout_ms:
                current_priority, current_exp = heapq.heappop(queue)

                if current_exp.value == target:
                    result = self._simplify_expression(current_exp.expr)
                    self.expression_cache[target_int] = result
                    return result

                operators = self._get_operators(target_int)
                random.shuffle(operators)

                for base_num, base_expr_str in self.base_number_map.items():
                    base_exp = Expression(base_num, base_expr_str, set(), None)
                    for op in operators:
                        # 正向计算
                        result = self._evaluate(current_exp, base_exp, op)
                        if result and result.value not in visited and self._is_worth_exploring(result.value, target, visited):
                            distance = abs(float(result.value - target))
                            heapq.heappush(queue, (distance, result))
                            visited.add(result.value)
                        
                        # 反向计算
                        if op in {'-', '/'}:
                            reverse_result = self._evaluate(base_exp, current_exp, op)
                            if reverse_result and reverse_result.value not in visited and self._is_worth_exploring(reverse_result.value, target, visited):
                                distance = abs(float(reverse_result.value - target))
                                heapq.heappush(queue, (distance, reverse_result))
                                visited.add(reverse_result.value)

        # 3. 如果BFS超时或目标数过大，则使用新的贪心分解算法
        large_number_expr = self._decompose_large_number(target)
        if large_number_expr:
            self.expression_cache[target_int] = large_number_expr
            return large_number_expr
        
        # 所有方法都失败
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
        tokens = re.findall(r'(√⑨|⑨{1,3}|\d+|\(|\)|\+|\-|\*|\/)', expr)
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
            return result
        return ""