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

try:
    import msvcrt  # Windows 系统可用
except ImportError:
    msvcrt = None

if sys.platform != 'win32':
    import tty
    import termios
else:
    tty = None
    termios = None

sys.stdout.reconfigure(encoding='utf-8')

@dataclass
class Expression:
    """表达式类，存储数值和对应的字符串表示"""
    value: float
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
        self._disable_divisions = False  # 新增属性
        self.base_numbers = {9, 99, 999}
        from audio_data import AUDIO_DATA
        self.AUDIO_DATA = AUDIO_DATA
        self.expression_cache: Dict[int, str] = {
    1017: '(9+999)+9',
    999: '(999*9)/9',
    2007: '(999*2)+9',
    1989: '(999*2)-9',
    1971: '(99*20)-9',
    5004: '(999*5)+9',
    4986: '(999*5)-9',
    4959: '(99*50)+9',
    9999: '(999*10)+9',
    9981: '(999*10)-9',
    10008: '(99*101)+9',
    9990: '(99*101)-9',
    108: '9+99',
    -90: '9-99',
    891: '99*9',
    1008: '9+999',
    -990: '9-999',
    8991: '9*999',
    90: '99-9',
    11: '99/9',
    1098: '99+999',
    -900: '99-999',
    990: '999-9',
    111: '999/9',
    900: '999-99',
    10998: '((999*10)+9)+999',
    9000: '(999*9)+9',
    10098: '((999*10)+9)+99',
    9900: '((999*10)+9)-99',
    101: '((999*10)+9)/99',
    89991: '((999*10)+9)*9',
    1111: '((999*10)+9)/9',
    10989: '(999/9)*99',
    10: '(99-9)/9',
    10089: '((99*101)-9)+99',
    9891: '((99*101)-9)-99',
    89910: '(99-9)*999',
    1110: '(999/9)+999',
    10980: '((999*10)-9)+999',
    8982: '(999*9)-9',
    10080: '((999*10)-9)+99',
    9882: '(999+99)*9',
    89829: '((999*10)-9)*9',
    9972: '((999*10)-9)-9',
    1109: '((999*10)-9)/9',
    7992: '(999*9)-999',
    9: '(9+99)-99',
    9090: '(9*999)+99',
    8892: '(999*9)-99',
    80919: '(999*9)*9',
    6003: '((999*5)+9)+999',
    4005: '((999*5)+9)-999',
    5103: '((999*5)+9)+99',
    4905: '((999*5)+9)-99',
    45036: '((999*5)+9)*9',
    5013: '((999*5)+9)+9',
    4995: '((999*5)-9)+9',
    556: '((999*5)+9)/9',
    5985: '((999*5)-9)+999',
    3987: '((999*5)-9)-999',
    5085: '((999*5)-9)+99',
    4887: '((999*5)-9)-99',
    44874: '((999*5)-9)*9',
    4977: '((999*5)-9)-9',
    554: '((999*5)-9)/9',
    5958: '((99*50)+9)+999',
    3960: '((99*50)+9)-999',
    5058: '((99*50)+9)+99',
    4860: '((99*50)+9)-99',
    44631: '((99*50)+9)*9',
    4968: '((99*50)+9)+9',
    4950: '((99*50)+9)-9',
    551: '((99*50)+9)/9',
    3006: '((999*2)+9)+999',
    2106: '((999*2)+9)+99',
    1908: '((999*2)+9)-99',
    18063: '((999*2)+9)*9',
    2016: '((999*2)+9)+9',
    1998: '((999*2)-9)+9',
    223: '((999*2)+9)/9',
    2988: '((99*20)+9)+999',
    2088: '((999*2)-9)+99',
    1890: '(99*9)+999',
    17901: '((999*2)-9)*9',
    1980: '((99*20)+9)-9',
    221: '((99*20)+9)/9',
    2970: '((99*20)-9)+999',
    972: '(99+9)*9',
    2070: '((99*20)-9)+99',
    1872: '((99*20)-9)-99',
    17739: '((99*20)-9)*9',
    1962: '((99*20)-9)-9',
    219: '((99*20)-9)/9',
    2097: '(99+999)+999',
    99: '(99*9)/9',
    1197: '(99+999)+99',
    1107: '(99+9)+999',
    1089: '(99/9)*99',
    122: '(999+99)/9',
    18: '((999+9)+9)-999',
    1116: '((999+9)+9)+99',
    918: '((999+9)+9)-99',
    9153: '((999+9)+9)*9',
    1026: '((999+9)+9)+9',
    113: '((999+9)+9)/9',
    99792: '(999+9)*99',
    909: '(999-99)+9',
    9072: '(9+999)*9',
    112: '(999+9)/9',
    1: '((999*9)/9)/999',
    98901: '((9*999)/9)*99',
    -1989: '(9-999)-999',
    -98010: '(9-999)*99',
    -891: '(99+9)-999',
    -1089: '(9-999)-99',
    -10: '(9-99)/9',
    -8910: '(9-99)*99',
    -981: '(9-999)+9',
    -999: '(9-999)-9',
    -110: '(9-999)/9',
    -9: '(99-9)-99',
    98010: '(999-9)*99',
    8910: '(999-9)*9',
    981: '(999-9)-9',
    110: '(99/9)+99',
    -1899: '(99-999)-999',
    -89100: '(99-999)*99',
    -801: '(99-999)+99',
    -8100: '(99-999)*9',
    -909: '(99-999)-9',
    -100: '(99-999)/9',
    1899: '(999-99)+999',
    -99: '(9-99)-9',
    89100: '(999-99)*99',
    801: '(999-99)-99',
    8100: '(999-99)*9',
    100: '(999-99)/9',
    -108: '(99*9)-999',
    88209: '(9*99)*99',
    792: '(9*99)-99',
    8019: '(99*9)*9',
    882: '(9*99)-9',
    -888: '(999/9)-999',
    210: '(999/9)+99',
    12: '(9+99)/9',
    120: '(999/9)+9',
    102: '(999/9)-9',
    10692: '(9+99)*99',
    207: '(9+99)+99',
    117: '(9+99)+9',
    -89910: '(9-99)*999',
    -189: '(9-99)-99',
    -810: '(9-99)*9',
    -81: '(9-99)+9',
    189: '(99-9)+99',
    810: '(99-9)*9',
    81: '(99-9)-9',
    1010: '(99/9)+999',
    -988: '(99/9)-999',
    -88: '(99/9)-99',
    20: '(99/9)+9',
    2: '(99/9)-9',
}
        self.precompute_range = range(1, 101)
        self.max_line_length = 60  # 调整行长度
        self._precompute_common_results()
        # 将缓存中的表达式转换为符号形式
        self.expression_cache = {k: v.replace('9', '⑨ ') for k, v in self.expression_cache.items()}

    def _user_wants_to_abort(self) -> bool | None:
        """
        检测用户是否按下任意键以中断搜索。
        支持 Windows 和 Unix 系统。
        """
        if sys.platform == 'win32':
            # Windows 系统
            if msvcrt.kbhit():
                # 清空输入缓冲区
                while msvcrt.kbhit():
                    msvcrt.getch()
                return True
        else:
            # Unix 系统
            if tty and termios:  # 确保模块已导入
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    # 设置超时时间为0，使read非阻塞
                    rlist, _, _ = select.select([sys.stdin], [], [], 0)
                    if rlist:
                        sys.stdin.read(1)
                        return True
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return False

    def play_baka_sound(self):
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

    def _precompute_common_results(self):
        print("预计算常用结果中...")
        # 先处理高频数字
        priority_targets = [k for k in self.expression_cache if 1 <= k <= 1000]
        for target in priority_targets:
            if target not in self.expression_cache:
                self._find_expression_with_timeout(target, timeout_ms=500)

        # 补充计算其他预定义范围
        for i in self.precompute_range:
            if i not in self.expression_cache:
                self._find_expression_with_timeout(i, timeout_ms=100)
        print("预计算完成！")

    def _find_expression_with_timeout(self, target: int, timeout_ms: int = 1000) -> Optional[str]:
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

        tokens = re.findall(r'(\d+|\(|\)|\+|\|\*|\|)', expr)
        tokens = [t for t in tokens if t]
        lines = []
        current_line = []
        current_length = 0

        for i, token in enumerate(tokens):
            new_length = current_length + len(token) + (1 if current_line else 0)

            # 长数字预判换行
            if len(token) > 4 and current_length > self.max_line_length // 2:
                self._split_line(current_line, lines)
                current_length = 0

            if new_length > self.max_line_length:
                split_pos = self._find_best_split_pos(current_line)
                if split_pos != -1:
                    head = current_line[:split_pos + 1]
                    tail = current_line[split_pos + 1:]
                    lines.append(''.join(head))
                    current_line = tail
                    current_length = sum(len(t) for t in tail) + len(tail) - 1
                else:
                    self._split_line(current_line, lines)
                    current_length = 0

            current_line.append(token)
            current_length += len(token) + (1 if current_line else 0)

        self._split_line(current_line, lines)

        wrapped = lines[0]
        for line in lines[1:]:
            wrapped += '\n    ' + line.lstrip('+-*/').lstrip()
        return wrapped

    def _find_expression_without_timeout(self, target: int) -> Optional[str]:
        """解除时间限制进行重试，并显示进度"""
        self._disable_divisions = False
        if target % 9 != 0:
            self._disable_divisions = True
        last_debug_time = time.time()

        queue: List[Tuple[float, Expression]] = []
        visited: Set[float] = set()
        attempts = 0  # 用来记录尝试的组合次数

        for num in self.base_numbers:
            expr_str = str(num).replace('9', '⑨ ')  # 替换基础数字为符号
            exp = Expression(float(num), str(num), set(), None)
            queue.append((self._estimate_distance(exp.value, target), exp))
            visited.add(exp.value)

        print("\n按任意键可以停止搜索...")

        start_time = time.time()

        while queue:

            # 添加用户中断检测：
            if self._user_wants_to_abort():
                print("\n检测到按键，中断搜索")
                print("\033[38;2;1;101;204mcirno\033[0m下次一定会算出来的！")
                print("琪露诺才不是baka！")
                return ""  # 或者直接退出程序，比如调用 sys.exit(0)

            queue.sort(key=lambda x: (
                x[0] * (0.8 if '*' in x[1].operators_used else 1),
                -self._diversity_score(x[1].operators_used)
            ))

            queue.sort(key=lambda x: (
                x[0] * (0.5 if '*' in x[1].operators_used else 1),
                -self._diversity_score(x[1].operators_used),
                len(x[1].expr)  # 优先短表达式
            ))

            # 调试信息输出（每隔5秒）
            current_time = time.time()
            if current_time - last_debug_time > 5:
                if queue:
                    # 获取当前最佳候选
                    best = min(queue, key=lambda x: abs(x[1].value - target))
                    print(f"搜索中... 当前最佳候选值：{best[1].value} (与目标差距：{abs(best[1].value - target)})")
                    last_debug_time = current_time  # 更新时间戳

            _, current_exp = queue.pop(0)

            # 每隔 1 秒更新一次进度
            if time.time() - start_time >= 1:
                print(f"已尝试{attempts}种组合，\033[38;2;1;101;204mcirno\033[0m正在努力搜索...")
                start_time = time.time()  # 重置时间

            if self._is_integer(current_exp.value) and round(current_exp.value) == target:
                result = self._simplify_expression(current_exp.expr)
                self.expression_cache[target] = result

                # 替换表达式中的所有 '9' 为 '⑨ '
                result_with_symbols = result.replace('9', '⑨ ')
                return result_with_symbols

            # 动态获取运算符列表
            operators = self._get_operators(target)
            random.shuffle(operators)

            for base_num in self.base_numbers:
                base_exp = Expression(float(base_num), str(base_num), set(), None)

                for op in operators:
                    result = self._evaluate(current_exp, base_exp, op)
                    if result and result.value not in visited and self._is_worth_exploring(result.value, target,visited):
                        queue.append((self._estimate_distance(result.value, target), result))
                        visited.add(result.value)

                    if op in {'-', '/'}:
                        reverse_result = self._evaluate(base_exp, current_exp, op)
                        if reverse_result and reverse_result.value not in visited and self._is_worth_exploring(
                                reverse_result.value, target, visited):
                            queue.append((self._estimate_distance(reverse_result.value, target), reverse_result))
                            visited.add(reverse_result.value)

            attempts += 1

        return "未找到有效表达式"

    def find_expression(self, target: int) -> str:
        result = self._find_expression_with_timeout(target)
        if result:
            # 如果原始表达式存在，转换为符号形式
            symbol_result = result.replace('9', '⑨ ')
            if symbol_result == "搜索已中断":
                # 用户中断了搜索，做相应处理
                return "搜索已中断，返回主菜单。"
            return symbol_result

        # 在这里询问用户是否解除时间限制重新尝试
        print("无法在1s内找到有效表达式。")
        while True:
            retry = input("是否解除时间限制重新尝试？（请输入y/n并按下回车确认）").strip().lower()
            if retry in ('y', 'n'):
                break
            print("请输入y或n")

        if retry == 'y':
            print("好的，正在尝试搜索：")
            return self._find_expression_without_timeout(target)
        else:
            print("好的,请在下方输入目标整数")
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
            target = int(user_input)
            start = time.time()
            expr = finder.find_expression(target)
            # 如果返回的结果既不是 "" 也不是用户中断的提示，则打印结果和 baka~
            if expr not in ["", "搜索已中断，返回主菜单。", "搜索已中断"]:
                print(f"\n结果 ({time.time() - start:.2f}s):")
                print(f"{target} = {expr}")
                # 使用 ANSI 转义码设置文字颜色为 #0165cc（RGB: 1,101,204），打印 "baka~"
                print("\033[38;2;1;101;204mbaka~\033[0m")
                finder.play_baka_sound()

            else:
                # 如果搜索中断或找不到结果，原样输出提示信息
                print(expr)
        except ValueError:
            print("请输入有效整数！")

if __name__ == "__main__":
    main()
