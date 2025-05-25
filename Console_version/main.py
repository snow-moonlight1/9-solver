from dataclasses import dataclass
from typing import Optional, Set, List, Tuple
import math
import time
import random
import re
import sys
import wave
import pyaudio
import io
import base64
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtGui import QPixmap, QImage, QScreen, QPaintEvent, QCloseEvent
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, pyqtSignal
from decimal import Decimal, getcontext
sys.stdout.reconfigure(encoding='utf-8')
getcontext().prec = 50
from fumo import FUMO


class FumoSplash(QWidget):
    splash_closed = pyqtSignal()
    def __init__(self, pixmap: QPixmap,                  
                 main_app_screen: Optional[QScreen] = None,
                 fallback_geometry: Optional[QRect] = None):
        super().__init__()
        # print(f"--- FumoSplash __init__ (Console Version) ---") # 可用于调试
        if pixmap is None or pixmap.isNull():
            print("  FumoSplash __init__: Invalid pixmap, aborting.")
            return 

        self.pixmap_original_size = pixmap.size()
        self.pixmap = pixmap
        self.main_app_screen = main_app_screen
        self.fallback_geometry = fallback_geometry # 主窗口的几何，或屏幕几何

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            # Qt.WindowType.SplashScreen # SplashScreen 可能需要 QApplication 更早存在
            Qt.WindowType.Tool # Tool 类型通常也能达到效果且更通用
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose) # 关键：动画后自动删除

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setWindowOpacity(0.0) 
        # print(f"  FumoSplash __init__: Initial windowOpacity set to 0.0")

        self.animation_group = QSequentialAnimationGroup(self)
        
        self.fade_in_duration = 200  
        self.hold_duration = 100     
        self.fade_out_duration = 200 

        self._setup_and_start_animation()

    def _setup_and_start_animation(self):
        # print(f"--- FumoSplash _setup_and_start_animation ---")
        fade_in_anim = QPropertyAnimation(self, b"windowOpacity")
        fade_in_anim.setDuration(self.fade_in_duration)
        fade_in_anim.setStartValue(0.0)
        fade_in_anim.setEndValue(1.0)
        fade_in_anim.setEasingCurve(QEasingCurve.Type.Linear)

        fade_out_anim = QPropertyAnimation(self, b"windowOpacity")
        fade_out_anim.setDuration(self.fade_out_duration)
        fade_out_anim.setStartValue(1.0)
        fade_out_anim.setEndValue(0.0)
        fade_out_anim.setEasingCurve(QEasingCurve.Type.Linear)

        self.animation_group.addAnimation(fade_in_anim)
        self.animation_group.addPause(self.hold_duration) 
        self.animation_group.addAnimation(fade_out_anim)

        self.animation_group.finished.connect(self._on_animation_finished_and_close) 

        # print(f"  Calling _randomize_size_and_position...")
        self._randomize_size_and_position() 
        # print(f"  Geometry after randomize: {self.geometry()}, Label pixmap size: {self.label.pixmap().size() if self.label.pixmap() else 'None'}")
        
        # print(f"  Calling self.show()...")
        self.show()
        # self.activateWindow() # 对于非交互式splash可能不需要
        self.raise_()         
        # print(f"  self.show() called. Is visible: {self.isVisible()}, Window Opacity: {self.windowOpacity()}")
        
        # print(f"  Starting animation group...")
        self.animation_group.start()
        # print(f"  Animation group state after start: {self.animation_group.state()}")

    # ---- 新增方法：当动画组完成时调用 ----
    def _on_animation_finished_and_close(self):
        self.close() # 调用 QWidget.close()

    def closeEvent(self, event: QCloseEvent): # 建议使用 QCloseEvent
        self.splash_closed.emit() # 发出我们自定义的关闭信号
        super().closeEvent(event) # 调用父类的 closeEvent 来实际关闭窗口
    
    def _randomize_size_and_position(self):
        if self.pixmap.isNull():
            return

        all_screens = QApplication.instance().screens()
        target_screen_geometry = None

        if not all_screens:
            print("  No screens available for FumoSplash.")
            if self.fallback_geometry: # 使用传入的主窗口几何作为最后手段
                target_screen_geometry = self.fallback_geometry
            else: # 如果连这个都没有，就没法定位了
                print("  No fallback geometry for FumoSplash, cannot position.")
                self.resize(100,100) # 设个默认大小，可能会在(0,0)显示
                return
        else:
            main_app_screen_obj = self.main_app_screen
            if main_app_screen_obj is None and all_screens: # 如果没传入主程序屏幕，就用系统主屏幕
                 main_app_screen_obj = QApplication.instance().primaryScreen() or all_screens[0]


            screens_to_choose_from = []
            weights = []
            main_screen_weight_target = 0.60
            
            if len(all_screens) == 1:
                main_screen_weight = 1.0 
                other_screen_weight_each = 0.0
            elif len(all_screens) == 2:
                main_screen_weight = main_screen_weight_target 
                other_screen_weight_each = 1.0 - main_screen_weight 
            elif len(all_screens) == 3:
                main_screen_weight = main_screen_weight_target 
                other_screen_weight_each = (1.0 - main_screen_weight) / 2 
            elif len(all_screens) == 4: 
                main_screen_weight = 0.58
                other_screen_weight_each = (1.0 - main_screen_weight) / 3 
            else: 
                main_screen_weight = 0.55 
                if len(all_screens) > 1:
                    other_screen_weight_each = (1.0 - main_screen_weight) / (len(all_screens) - 1)
                else: 
                    other_screen_weight_each = 0 

            for screen in all_screens:
                screens_to_choose_from.append(screen)
                if main_app_screen_obj and screen.name() == main_app_screen_obj.name():
                    weights.append(main_screen_weight)
                else:
                    weights.append(other_screen_weight_each)
            
            if not weights or all(w == 0 for w in weights):
                chosen_screen = random.choice(all_screens)
            else:
                chosen_screen_list = random.choices(screens_to_choose_from, weights=weights, k=1)
                chosen_screen = chosen_screen_list[0]
            
            target_screen_geometry = chosen_screen.geometry()
            # print(f"  Chosen screen (weighted): '{chosen_screen.name()}', Geometry: {target_screen_geometry}")

        # ---- 随机大小计算 ----
        screen_min_dim = min(target_screen_geometry.width(), target_screen_geometry.height())
        min_scale_percent = 0.20 
        max_scale_percent = 0.60 
        min_allowed_size_on_screen = int(screen_min_dim * min_scale_percent)
        max_allowed_size_on_screen = int(screen_min_dim * max_scale_percent)
        target_fumo_dimension = random.randint(min_allowed_size_on_screen, max_allowed_size_on_screen)
        
        original_width = self.pixmap_original_size.width()
        original_height = self.pixmap_original_size.height()

        if original_width == 0 or original_height == 0: 
            scaled_width, scaled_height = 100, 100 
        elif original_width >= original_height: 
            scale_factor = target_fumo_dimension / original_height 
            scaled_height = target_fumo_dimension
            scaled_width = int(original_width * scale_factor)
        else: 
            scale_factor = target_fumo_dimension / original_width 
            scaled_width = target_fumo_dimension
            scaled_height = int(original_height * scale_factor)

        scaled_width = min(scaled_width, original_width)
        scaled_height = min(scaled_height, original_height)
        scaled_width = max(scaled_width, 50) 
        scaled_height = max(scaled_height, 50)
        # print(f"  Calculated Fumo scaled size: {scaled_width}x{scaled_height}")

        self.label.setPixmap(self.pixmap.scaled(scaled_width, scaled_height, 
                                                Qt.AspectRatioMode.KeepAspectRatio, 
                                                Qt.TransformationMode.SmoothTransformation))
        self.resize(scaled_width, scaled_height) 
        
        # ---- 随机位置计算 ----
        max_x_offset_on_screen = target_screen_geometry.width() - scaled_width
        max_y_offset_on_screen = target_screen_geometry.height() - scaled_height
        rand_x_on_screen_offset = random.randint(0, max_x_offset_on_screen) if max_x_offset_on_screen > 0 else 0
        rand_y_on_screen_offset = random.randint(0, max_y_offset_on_screen) if max_y_offset_on_screen > 0 else 0
            
        final_screen_x = target_screen_geometry.x() + rand_x_on_screen_offset
        final_screen_y = target_screen_geometry.y() + rand_y_on_screen_offset
        # print(f"  Calculated final screen position: X={final_screen_x}, Y={final_screen_y}")
        self.move(final_screen_x, final_screen_y)

    def paintEvent(self, event: QPaintEvent): 
        super().paintEvent(event)

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
    # 将 FUMO 常量直接赋值给类属性
    FUMO_IMAGE_DATA_BASE64 = FUMO 

    def __init__(self): # 确保是 __init__
        self._disable_divisions = False
        self.base_numbers = {Decimal('9'), Decimal('99'), Decimal('999')}
        from audio_data import AUDIO_DATA
        self.AUDIO_DATA = AUDIO_DATA
        self.large_number_threshold = 5000
        from expression_cache import EXPRESSION_CACHE
        self.expression_cache = EXPRESSION_CACHE
        self.expression_cache = {k: v.replace('9', '⑨') for k, v in self.expression_cache.items()} # 移除了⑨后的空格
        
        self.show_fumo_splash = True 
        self.fumo_pixmap = None
        self.active_fumo_splash = None

        # ---- 修改 Fumo 图片加载逻辑 ----
        # 检查 FUMO_IMAGE_DATA_BASE64 是否是一个非空字符串
        if isinstance(self.FUMO_IMAGE_DATA_BASE64, str) and self.FUMO_IMAGE_DATA_BASE64:
            try:
                fumo_image_data = base64.b64decode(self.FUMO_IMAGE_DATA_BASE64)
                fumo_image = QImage.fromData(fumo_image_data)
                if not fumo_image.isNull():
                    self.fumo_pixmap = QPixmap.fromImage(fumo_image)
            except Exception as e:
                print(f" [错误] 加载Fumo图像失败: {e}")
        else:
            print(" [提示] FUMO_IMAGE_DATA_BASE64 未提供有效数据，Fumo彩蛋将不可用。")

    def _trigger_fumo_splash_display(self): 
        if not self.show_fumo_splash or self.fumo_pixmap is None or self.fumo_pixmap.isNull():
            return

        q_app = QApplication.instance() # <--- 将 app 重命名为 q_app 避免与内置冲突，并获取实例
        if q_app is None:
            print("  QApplication not running, cannot display Fumo splash.")
            # 如果 QApplication 在 main() 中总是被创建，这里理论上不应该为 None
            # 但作为安全检查是好的。
            return
            
        if self.active_fumo_splash is not None and self.active_fumo_splash.isVisible():
            print("  一个FumoSplash已经在显示中，跳过新的。")
            # 可选：或者强制关闭旧的，再创建新的
            # self.active_fumo_splash.close() 
            # self.active_fumo_splash = None
            return 

        current_active_screen = q_app.primaryScreen() 
        # 对于控制台，我们可能没有一个“活动窗口”的概念来获取其屏幕
        # 使用 primaryScreen 是一个合理的默认值
        if not current_active_screen: # 如果连主屏幕都没有（非常罕见）
            all_screens = q_app.screens()
            if all_screens:
                current_active_screen = all_screens[0]
            else:
                print("  No screens available for FumoSplash positioning.")
                return

         # 创建新的 FumoSplash 实例
        new_splash = FumoSplash(
            self.fumo_pixmap, 
            main_app_screen=current_active_screen, 
            fallback_geometry=current_active_screen.geometry() if current_active_screen else QRect(0,0,800,600)
        )
        self.active_fumo_splash = new_splash # <--- 存储对新实例的引用
        new_splash.splash_closed.connect(self.clear_active_fumo_splash_reference)

    def play_baka_sound(self):
        # 先尝试显示 Fumo
        self._trigger_fumo_splash_display() # <--- 调用新的 Fumo 显示方法

        # 然后在线程中播放声音
        thread = threading.Thread(target=self._play_audio, daemon=True)
        thread.start()    

    def clear_active_fumo_splash_reference(self): # <--- 新增方法
        self.active_fumo_splash = None

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

    def find_expression(self, target: int) -> str:
        result = self._find_expression_with_timeout(target)
        if result:
            # 如果原始表达式存在，转换为符号形式
            symbol_result = result.replace('9', '⑨ ')
            return symbol_result
        return ""


def main():
    app_args = sys.argv if hasattr(sys, 'argv') else ['']
    q_app = QApplication.instance()
    if q_app is None:
        q_app = QApplication(app_args)

    finder = ImprovedNineExpressionFinder()

    print("\n欢迎使用⑨ 表达式求解器！")
    print("\nF/NF 控制Fumo, q退出")
    # ... (打印提示) ...

    while True:
        # ---- 在每次 input 前处理一次事件 ----
        if q_app: # 确保 q_app 存在
            q_app.processEvents()
        # ----------------------------------
        user_input = input("\n请输入目标整数:").strip()

        if user_input.lower() == 'q' or user_input.lower() == 'quit':
            print("\033[38;2;1;101;204mbaka~\033[0m")
            finder.play_baka_sound()
            if finder.show_fumo_splash and finder.fumo_pixmap and q_app: # 检查q_app
                 for _ in range(60): # 处理事件约0.6秒
                     q_app.processEvents()
                     time.sleep(0.01)
            else:
                 time.sleep(0.5)
            break

        elif user_input.upper() == 'F':
            finder.show_fumo_splash = True
            print("Fumo彩蛋 (GUI窗口) 已开启！")
            continue
        elif user_input.upper() == 'NF':
            finder.show_fumo_splash = False
            print("Fumo彩蛋 (GUI窗口) 已关闭。")
            continue

        try:
            # ... (解析 target) ...
            if 'e' in user_input.lower(): target = int(float(user_input))
            else: target = int(user_input)

            print(f"正在为 {target} 寻找表达式...")
            start_time = time.time()
            expr = finder.find_expression(target)
            elapsed_time = time.time() - start_time

            if expr:
                print(f"\n结果 ({elapsed_time:.2f}s):")
                # wrapped_expr = finder._wrap_expression(expr)
                print(f"{target} = {expr}") # 直接打印原始表达式
                print("\033[38;2;1;101;204mbaka~\033[0m")
                finder.play_baka_sound()

                if finder.show_fumo_splash and finder.fumo_pixmap and q_app: # 检查q_app
                    # 给 Fumo Splash 动画一些时间运行
                    # 可以用一个短循环来处理事件，而不是长 sleep
                    # 总共等待约 0.5 - 0.6 秒 (Fumo动画总时长)
                    for _ in range(55): # 大约 0.55 秒
                        q_app.processEvents()
                        time.sleep(0.01) # 短暂休眠，让其他线程（如音频）也有机会
            else:
                print(f"未能找到 {target} 的表达式。")
        except ValueError:
            print("请输入有效整数或科学计数法(如1e3)！")
        except Exception as e:
            print(f"发生意外错误: {e}")

    # ---- 在主循环结束后，可以考虑退出QApplication (如果它是唯一用途) ----
    # if q_app:
    # q_app.quit() # 这会终止事件循环，如果它是通过 exec() 启动的
    # 对于非exec启动的，它可能不会做太多事，但清理总是好的
    # -----------------------------------------------------------------

if __name__ == "__main__":
    main()