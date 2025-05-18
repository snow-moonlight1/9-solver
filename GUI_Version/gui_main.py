# gui_main.py
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QSizePolicy, 
                             QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QEvent
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QPalette, QImage
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from main import ImprovedNineExpressionFinder
from Icon_Data import ICON_DATA
import time
import base64


def get_system_theme():
    """检测系统主题（浅色或深色）"""
    palette = QApplication.instance().palette()
    # 我们通过比较窗口背景色的亮度来判断
    # QPalette.ColorRole.Window 是大多数窗口部件的背景色
    # lightness() 返回一个 0 (黑) 到 255 (白) 的值
    if palette.color(QPalette.ColorRole.Window).lightness() < 128:
        return "dark"
    else:
        return "light"

# 背景色常量
LIGHT_ACTIVE_BG = "#f0f4f9"
LIGHT_INACTIVE_BG = "#f3f3f3"
DARK_ACTIVE_BG = "#1a212d"
DARK_INACTIVE_BG = "#202020"

# 浅色主题样式表
LIGHT_STYLESHEET_BASE ="""
    QMainWindow {
        /* background-color 将由事件动态设置 */
    }
    QLabel {
        color: #495057; /* 深色文字 */
    }
    QPushButton {
        background-color: #4a90e2;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 14px;
        min-width: 60px;
        max-width: 80px;
    }
    QPushButton:hover {
        background-color: #3a7bc8;
    }
    QPushButton:disabled {
        background-color: #cccccc;
    }
    QLineEdit {
        padding: 8px;
        border: 1px solid #ced4da;
        border-radius: 4px;
        font-size: 16px;
        background-color: white;
        color: #212529; /* 输入框文字颜色 */
    }
    QLineEdit:focus {
        border: 1px solid #4a90e2;
        background-color: #f8fbff;
    }
    QTextEdit {
        padding: 12px;
        border: 1px solid #ced4da;
        border-radius: 4px;
        font-family: Consolas, 'Courier New', monospace;
        font-size: 14px;
        background-color: white;
        color: #212529; /* 文本编辑区默认文字颜色 */
    }
    #main_frame {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    #status_label { /* 确保状态栏标签有特定样式 */
        color: #6c757d;
        font-style: italic;
    }
    /* 以下是你已有的特殊颜色，浅色模式下保持不变或微调 */
    NineSolverGUI #title_label { /* 更精确地指定标题标签 */
        color: #4a90e2; margin-bottom: 10px;
    }
    NineSolverGUI #description { /* 更精确地指定描述标签 */
        color: #6c757d; font-size: 14px;
    }
    NineSolverGUI #separator {
        color: #e9ecef;
    }
    NineSolverGUI #result_title {
        font-size: 16px; font-weight: bold; color: #343a40;
    }
"""

# 深色主题样式表
DARK_STYLESHEET_ACTIVE_BASE = """
    QMainWindow {
        /* background-color 将由事件动态设置 */
    }
    QLabel {
        color: #b0c4de; /* 浅蓝灰色文字 */
    }
    QPushButton {
        background-color: #4682b4; /* 钢蓝色按钮 */
        color: white; /* 文字保持白色 */
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 14px;
        min-width: 60px;
        max-width: 80px;
    }
    QPushButton:hover {
        background-color: #3a6b94;
    }
    QPushButton:disabled {
        background-color: #3d4a56;
        color: #7f8c9a;
    }
    QLineEdit {
        padding: 8px;
        border: 1px solid #4a5d6e; /* 蓝灰色边框 */
        border-radius: 4px;
        font-size: 16px;
        background-color: #2d3846; /* 深蓝灰色输入框背景 */
        color: #b0c4de; /* 浅蓝灰色文字 */
    }
    QLineEdit:focus {
        border: 1px solid #5f9ea0; /* 卡其色高亮边框 */
        background-color: #3a4b5c;
    }
    QTextEdit {
        padding: 12px;
        border: 1px solid #4a5d6e; /* 蓝灰色边框 */
        border-radius: 4px;
        font-family: Consolas, 'Courier New', monospace;
        font-size: 14px;
        background-color: #2d3846; /* 深蓝灰色文本编辑区背景 */
        color: #b0c4de; /* 浅蓝灰色默认文字 */
    }
    #main_frame {
        background-color: #2a3542; /* 深蓝灰色背景 */
        border-radius: 8px;
        border: 1px solid #3a4b5c; /* 蓝灰色边框 */
    }
    #status_label { /* 确保状态栏标签有特定样式 */
        color: #8fbc8f; /* 浅海绿色文字 */
        font-style: italic;
    }
    /* 深色模式下的特殊颜色调整 */
    NineSolverGUI #title_label { /* 更精确地指定标题标签 */
        color: #5f9ea0; margin-bottom: 10px; /* 卡其色标题 */
    }
    NineSolverGUI #description { /* 更精确地指定描述标签 */
        color: #8fbc8f; font-size: 14px; /* 浅海绿色描述 */
    }
    NineSolverGUI #separator {
        color: #3a4b5c; /* 蓝灰色分隔线 */
    }
    NineSolverGUI #result_title {
        font-size: 16px; font-weight: bold; color: #5f9ea0; /* 卡其色结果标题 */
    }
"""

# 深色主题 - 非激活状态 (调整版)
DARK_STYLESHEET_INACTIVE_BASE = """
    /* QMainWindow background will be #202020 */
    QLabel { 
        color: #9098a3; /* 比激活状态的 #b0c4de 略暗和灰一些 */
    }
    QPushButton {
        background-color: #3e688f; /* 比激活的 #4682b4 略暗和去饱和 */
        color: #d0d0d0; /* 文字颜色也略暗一点 */
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 14px;
        min-width: 60px; /* 确保与激活状态一致 */
        max-width: 80px; /* 确保与激活状态一致 */
    }
    QPushButton:hover {
        background-color: #365c7d; /* hover 状态也相应调整 */
    }
    QPushButton:disabled {
        background-color: #303840; /* 比激活的 #3d4a56 略暗 */
        color: #707880;    /* 比激活的 #7f8c9a 略暗 */
    }
    QLineEdit {
        padding: 8px;
        border: 1px solid #404f5d; /* 比激活的 #4a5d6e 略暗 */
        border-radius: 4px;
        font-size: 16px;
        background-color: #28303a; /* 比激活的 #2d3846 略暗 */
        color: #a0abb3;       /* 比激活的 #b0c4de 略暗和灰 */
    }
    QLineEdit:focus {
        border: 1px solid #4f7b7e; /* 比激活的 #5f9ea0 略暗 */
        background-color: #323f4b; /* 比激活的 #3a4b5c 略暗 */
    }
    QTextEdit {
        padding: 12px;
        border: 1px solid #404f5d; 
        border-radius: 4px;
        font-family: Consolas, 'Courier New', monospace;
        font-size: 14px;
        background-color: #28303a; 
        color: #a0abb3;
    }
    #main_frame {
        background-color: #262e38; /* 比激活的 #2a3542 略暗 */
        border-radius: 8px;
        border: 1px solid #323f4b; /* 比激活的 #3a4b5c 略暗 */
    }
    #status_label { 
        color: #7a997a; /* 比激活的 #8fbc8f 略暗和灰 */
        font-style: italic; 
    }
    NineSolverGUI #title_label { 
        color: #528b8b; /* 比激活的 #5f9ea0 略暗 */
        margin-bottom: 10px; 
    }
    NineSolverGUI #description { 
        color: #7a997a; 
        font-size: 14px; 
    }
    NineSolverGUI #separator { 
        color: #323f4b; 
    }
    NineSolverGUI #result_title { 
        font-size: 16px; 
        font-weight: bold; 
        color: #528b8b; 
    }
"""

class WorkerThread(QThread):
    result_ready = pyqtSignal(str, str, float)
    error_occurred = pyqtSignal(str)

    def __init__(self, target):
        super().__init__()
        self.target = target

    def run(self):
        try:
            finder = ImprovedNineExpressionFinder()
            start = time.time()
            expr = finder.find_expression(self.target)
            elapsed = time.time() - start
            self.result_ready.emit(str(self.target), expr, elapsed)
        except Exception as e:
            self.error_occurred.emit(str(e))
            

class AnimatedPushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation_group = QSequentialAnimationGroup(self)
        
        # 按下动画
        self.press_anim = QPropertyAnimation(self, b"geometry")
        self.press_anim.setDuration(80)
        self.press_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 释放动画
        self.release_anim = QPropertyAnimation(self, b"geometry")
        self.release_anim.setDuration(120)
        self.release_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        
        self.animation_group.addAnimation(self.press_anim)
        self.animation_group.addAnimation(self.release_anim)
        self.original_geometry = self.geometry()
        
    def triggerAnimation(self):
        if self.animation_group.state() != QPropertyAnimation.State.Running:
            self.press_anim.setStartValue(self.original_geometry)
            self.press_anim.setEndValue(self.original_geometry.adjusted(0, 3, 0, 3))
            self.release_anim.setStartValue(self.original_geometry.adjusted(0, 3, 0, 3))
            self.release_anim.setEndValue(self.original_geometry)
            self.animation_group.start()
            
    def mousePressEvent(self, event):
        self.triggerAnimation()
        super().mousePressEvent(event)
        
    def resizeEvent(self, event):
        self.original_geometry = self.geometry()
        super().resizeEvent(event)

class NineSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = get_system_theme() # 获取初始系统主题
        self._theme_initialized = False # 添加一个标志位        
        # 初始化系统托盘
        self.tray_icon = QSystemTrayIcon(self)
        self.ICON_DATA = ICON_DATA  
        # 新增：存储最后一次成功计算的结果
        self._last_target = None
        self._last_expression = None
        self._last_elapsed_time = None
        self.tray_icon.setIcon(QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(self.ICON_DATA)))))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示")
        show_action.triggered.connect(self.show_normal)
        quit_action = tray_menu.addAction("退出")
        quit_action.triggered.connect(QApplication.instance().quit)
        self.tray_icon.setContextMenu(tray_menu)
        
        # 连接托盘图标点击事件
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.setWindowTitle("⑨")
        self.setMinimumSize(800, 600)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(self.ICON_DATA)))))
        self.init_ui()
        self.setup_animations()

        # 连接系统调色板变化信号
        QApplication.instance().paletteChanged.connect(self.handle_theme_change)
        
    # 在 NineSolverGUI 类中
    def showEvent(self, event_obj: QEvent):
        """窗口第一次显示时，应用完整的主题并强制使用激活样式。"""
        super().showEvent(event_obj) 
        if not self._theme_initialized: # 使用你已有的标志位 _theme_initialized
            print("showEvent: Applying initial theme (forcing active style).")
            self.apply_theme_styling(self.current_theme, force_active_on_initial_show=True) 
            self._theme_initialized = True
    # 在 NineSolverGUI 类中的 event 方法
    def event(self, event_obj: QEvent):
        if event_obj.type() == QEvent.Type.WindowActivate:
            if self._theme_initialized: 
                self._update_activation_styles(is_active=True) # <--- 调用新方法名
        elif event_obj.type() == QEvent.Type.WindowDeactivate:
            if self._theme_initialized:
                self._update_activation_styles(is_active=False) # <--- 调用新方法名
        return super().event(event_obj)              

    def _update_activation_styles(self, is_active: bool):
        """根据窗口激活状态更新样式（背景色，以及深色模式下的组件）。"""
        # print(f"_update_activation_styles: Active: {is_active}. Current theme: {self.current_theme}")
        if not hasattr(self, 'current_theme') or not self._theme_initialized: # 确保主题已初始化
            return

        current_main_window_bg = ""
        current_base_stylesheet = ""

        if self.current_theme == "dark":
            current_main_window_bg = DARK_ACTIVE_BG if is_active else DARK_INACTIVE_BG
            # 关键：当激活状态改变时，深色模式的组件样式也需要切换
            current_base_stylesheet = DARK_STYLESHEET_ACTIVE_BASE if is_active else DARK_STYLESHEET_INACTIVE_BASE
        else: # light theme
            current_main_window_bg = LIGHT_ACTIVE_BG if is_active else LIGHT_INACTIVE_BG
            current_base_stylesheet = LIGHT_STYLESHEET_BASE # 浅色模式组件样式不变
        
        main_window_bg_style = f"QMainWindow {{ background-color: {current_main_window_bg}; }}"
        final_stylesheet = f"{main_window_bg_style}\n{current_base_stylesheet}"
        
        self.setStyleSheet(final_stylesheet)
        # self.update()
    # 在 NineSolverGUI 类中
    def handle_theme_change(self):
        """处理系统调色板变化事件（通常是浅色/深色模式切换）。"""
        new_system_theme = get_system_theme()
        print(f"paletteChanged: Detected system theme '{new_system_theme}', current GUI theme '{self.current_theme}'")
        
        # 只有当系统主题（浅色/深色）确实改变时才重新应用
        if new_system_theme != self.current_theme:
            print(f"System theme changed from '{self.current_theme}' to '{new_system_theme}'. Re-applying styles.")
            # 注意：apply_theme_styling 内部会更新 self.current_theme
            self.apply_theme_styling(new_system_theme) # 不传递 force_active_on_initial_show
                                                       # 或者显式传递 False: force_active_on_initial_show=False
                                                       # 默认是 False，所以不传也行。
        # 可选：如果主题没变，但某些情况想刷新激活状态（但event()应该处理了）
        # elif self._theme_initialized:
        # self._update_activation_styles(self.isActiveWindow()) 
    def apply_theme_styling(self, theme_name: str, force_active_on_initial_show: bool = False):
        """应用指定的主题样式表，并根据激活状态设置QMainWindow背景色和组件样式。"""
        
        # 1. 更新当前主题记录 (确保这是第一步或早期步骤)
        self.current_theme = theme_name 
        
        # 2. 确定激活状态
        is_active = self.isActiveWindow()
        if force_active_on_initial_show:
            is_active = True # 强制为激活状态
            print(f"apply_theme_styling: Forcing active state for theme '{self.current_theme}' during initial show.")
        else:
            print(f"apply_theme_styling: Applying theme '{self.current_theme}'. Active from isActiveWindow(): {is_active}")

        # 3. 根据主题和激活状态选择样式
        current_main_window_bg = ""
        current_base_stylesheet = ""

        if self.current_theme == "dark":
            current_main_window_bg = DARK_ACTIVE_BG if is_active else DARK_INACTIVE_BG
            current_base_stylesheet = DARK_STYLESHEET_ACTIVE_BASE if is_active else DARK_STYLESHEET_INACTIVE_BASE
        else: # light theme
            current_main_window_bg = LIGHT_ACTIVE_BG if is_active else LIGHT_INACTIVE_BG
            current_base_stylesheet = LIGHT_STYLESHEET_BASE
        
        # 4. 构建并应用最终样式表
        main_window_bg_style = f"QMainWindow {{ background-color: {current_main_window_bg}; }}"
        final_stylesheet = f"{main_window_bg_style}\n{current_base_stylesheet}"
        self.setStyleSheet(final_stylesheet)
        
        # 5. 其他更新
        self.stop_loading_animation()
        self.update() # 通常 setStyleSheet 会处理这个，但为了确保，我们也可以显式调用
        # QApplication.processEvents() # 先注释掉，看是否需要
        self._render_result_display() #主题切换后重新渲染结果
    def init_ui(self):
        # 主部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(10)
        
        self.title_label = QLabel("⑨ 表达式求解器")
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        title_layout.addWidget(self.title_label)
        
        self.description = QLabel("输入一个整数，琪露诺会尝试用9、99、999的加减乘除组合来表示它")
        self.description.setObjectName("description")
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(self.description)
        main_layout.addLayout(title_layout)
        
        # 主内容区域
        self.main_frame = QWidget()
        self.main_frame.setObjectName("main_frame")
        frame_layout = QVBoxLayout(self.main_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(20)
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("示例: 123, -456, 1e3")
        self.input_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        input_layout.addWidget(self.input_field)
        
        self.calculate_btn = AnimatedPushButton("计算")
        self.calculate_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.calculate_btn.clicked.connect(self.start_calculation)
        input_layout.addWidget(self.calculate_btn)
        
        frame_layout.addLayout(input_layout)
        
        
        # 分隔线
        self.separator = QFrame()
        self.separator.setObjectName("separator")
        self.separator.setFrameShape(QFrame.Shape.HLine)
        frame_layout.addWidget(self.separator)
        
        # 结果区域
        self.result_title = QLabel("计算结果")
        self.result_title.setObjectName("result_title")
        frame_layout.addWidget(self.result_title)
        
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        frame_layout.addWidget(self.result_display)
        
        main_layout.addWidget(self.main_frame)
        
        # 底部状态栏
        self.status_bar = self.statusBar()
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("status_label")
        self.status_bar.addPermanentWidget(self.status_label)
        
        # 连接回车键
        self.input_field.returnPressed.connect(self.on_enter_pressed)

        
    def show_result(self, target_str: str, expr: str, elapsed: float): # 添加类型提示
        self.stop_loading_animation()
        
        # 存储结果，以便主题切换时可以重绘
        self._last_target = target_str
        self._last_expression = expr
        self._last_elapsed_time = elapsed
        
        self._render_result_display() # 调用新的辅助方法来渲染显示

        if expr: # 只有成功找到表达式才播放声音和更新状态
            self.status_label.setText(f"计算完成 - 耗时 {elapsed:.2f}秒")
            finder = ImprovedNineExpressionFinder() # 实例化可以放在外面如果不需要每次新建
            finder.play_baka_sound()
        else:
            self.status_label.setText("未找到结果")

    # 在 NineSolverGUI 类中添加
    def _render_result_display(self):
        """根据存储的最后结果和当前主题，重新渲染结果显示区域。"""
        if self._last_target is None or self._last_expression is None or self._last_elapsed_time is None:
            # 如果没有存储的结果（比如程序刚启动，或上次计算失败/清空了），则不执行或显示提示
            # self.result_display.setPlainText("无计算结果可显示。") # 或者保持为空
            return

        target_str = self._last_target
        expr = self._last_expression
        elapsed = self._last_elapsed_time

        # 根据当前主题确定文本和特定颜色
        # 注意：这里的 default_text_color 应该由 QTextEdit 的全局样式表控制
        # 我们主要关心 HTML 内联样式中的特殊颜色
        # QTextEdit 的 stylesheet 已经有 color: #e0e0e0 (dark) 或 color: #212529 (light)
        # 所以 div 的 color 可以不设置，或者设置为 transparent/inherit，让父级控制
        # 但为了明确，我们可以继续设置它，或者确保它与QTextEdit的默认颜色一致
        
        # HTML div 的主文字颜色，应与 QTextEdit 的 stylesheet color 属性一致
        html_default_text_color = "#b0c4de" if self.current_theme == "dark" else "#495057" 
                                   # ^-- 使用 DARK_STYLESHEET_ACTIVE_BASE 中 QLabel 的颜色
                                   # 或者 DARK_STYLESHEET_INACTIVE_BASE 中 QLabel 的颜色
                                   # 取决于你希望 QTextEdit 的默认文字颜色是什么。
                                   # 通常，它会继承自 QTextEdit 的 stylesheet 设置。
                                   # 为了安全，我们这里明确指定。
                                   # 注意：你之前用的是 #e0e0e0 (dark) 和 #212529 (light) for default_text_color
                                   # 我们需要保持一致性。

        # 我们参照 QTextEdit 在主题样式表中的 `color` 属性
        if self.current_theme == "dark":
            if self.isActiveWindow():
                html_default_text_color = "#b0c4de" # Dark active QTextEdit color
            else:
                html_default_text_color = "#a0abb3" # Dark inactive QTextEdit color
        else: # light
            html_default_text_color = "#212529" # Light QTextEdit color

        # 特殊颜色
        time_color = "#aaaaaa" if self.current_theme == "dark" else "#6c757d" # 这些可以保持
        # expr_color 在你的代码中是 #ffffff (dark) 和 #000000 (light)
        # 这个颜色是你特别为表达式结果设置的，应该保留
        expr_color_html = "#ffffff" if self.current_theme == "dark" else "#000000"
        baka_color = "#2c9fff" if self.current_theme == "dark" else "#0165cc"

        if expr: # 确保表达式存在
            self.result_display.setHtml(f"""
                <div style="font-family: Consolas, 'Courier New', monospace; font-size: 14px; color: {html_default_text_color};">
                    <p>目标: <span style="font-weight: bold;">{target_str}</span></p>
                    <p>结果 (<span style="color: {time_color};">{elapsed:.2f}秒</span>):</p>
                    <p><span style="font-weight: bold;">{target_str}</span> = <span style="color: {expr_color_html};">{expr}</span></p>
                    <p style="color: {baka_color}; font-weight: bold;">baka~</p>
                </div>
            """)
        else: # 如果之前的结果是 "未找到表达式"
             # QTextEdit 的全局样式会处理文本颜色
            self.result_display.setPlainText(f"无法找到 {target_str} 的有效表达式")   
    def on_enter_pressed(self):
        self.calculate_btn.triggerAnimation()
        self.calculate_btn.click()
        
    def setup_animations(self):
        # 状态栏加载动画
        self.loading_animation = QPropertyAnimation(self.status_label, b"styleSheet")
        self.loading_animation.setDuration(500)
        self.loading_timer = self.startTimer(500)  # 每500ms切换一次状态
        self.loading_state = 0
        
    def start_calculation(self):
         # 清空之前的结果，因为要开始新的计算
        self._last_target = None
        self._last_expression = None
        self._last_elapsed_time = None
        # self.result_display.clear() # 也可以在这里清空显示，或者让 "计算中..." 覆盖
        input_text = self.input_field.text().strip()
        
        if input_text.lower() in ['q', 'quit']:
            self.close()
            return
            
        try:
            if 'e' in input_text.lower():
                target = int(float(input_text))
            else:
                target = int(input_text)
                
            self.calculate_btn.setEnabled(False)
            self.result_display.setPlainText("计算中，请稍候...")
            self.status_label.setText("正在计算...")
            
            # 启动加载动画
            self.start_loading_animation()
            
            # 创建工作线程
            self.worker = WorkerThread(target)
            self.worker.result_ready.connect(self.show_result)
            self.worker.error_occurred.connect(self.show_error)
            self.worker.finished.connect(self.cleanup_after_calculation)
            self.worker.start()
            
        except ValueError:
            self.result_display.setPlainText("错误: 请输入有效整数或科学计数法(如1e3)")
            self.status_label.setText("输入错误")
            self.input_field.clear()
    
    def start_loading_animation(self):
        """状态栏加载动画"""
        if self.current_theme == "dark":
            color1 = QColor("#aaaaaa") # 深色模式下的颜色1
            color2 = QColor("#cccccc") # 深色模式下的颜色2
        else:
            color1 = QColor("#6c757d") # 浅色模式下的颜色1
            color2 = QColor("#adb5bd") # 浅色模式下的颜色2
        
        self.loading_animation.stop()
        # 注意：QPropertyAnimation(self.status_label, b"styleSheet") 可能会与全局样式冲突
        # 更好的做法是动画 QGraphicsOpacityEffect 或者直接改变颜色属性（如果支持）
        # 但对于颜色，直接设置 styleSheet 片段是常见的
        # 为了让动画效果更平滑，我们可以让它只改变颜色部分
        # 但 QPropertyAnimation 对 styleSheet 的支持有限，它会整个替换 styleSheet 字符串
        # 所以，我们让它在两种固定样式间切换，或者直接改变文字颜色
        # 这里我们保持原有的机制，但颜色根据主题来
        
        # 如果是直接操作颜色属性，可以这样做，但 QLabel 没有直接的 color 属性可供动画
        # self.loading_animation = QPropertyAnimation(self.status_label, b"palette")
        # pal = self.status_label.palette()
        # pal.setColor(QPalette.ColorRole.WindowText, color1)
        # self.loading_animation.setStartValue(pal)
        # pal.setColor(QPalette.ColorRole.WindowText, color2)
        # self.loading_animation.setEndValue(pal)
        
        # 当前实现是改变 stylesheet，确保它只改变颜色
        # 但这可能不是最佳实践，因为 QPropertyAnimation 对 stylesheet 的插值可能不理想
        # 一个更简单的方式，但可能不是平滑动画：
        # 使用 QTimer 周期性地切换颜色，而不是 QPropertyAnimation
        
        # 沿用之前的逻辑，但颜色动态
        self.loading_animation.setKeyValueAt(0, f"color: {color1.name()}; font-style: italic;")
        self.loading_animation.setKeyValueAt(0.5, f"color: {color2.name()}; font-style: italic;")
        self.loading_animation.setKeyValueAt(1, f"color: {color1.name()}; font-style: italic;")
        self.loading_animation.setLoopCount(-1) # 无限循环
        self.loading_animation.start()
    
    def stop_loading_animation(self):
        """停止加载动画并恢复状态标签的正确颜色"""
        self.loading_animation.stop()
        # 恢复到主题对应的静态颜色
        if self.current_theme == "dark":
            self.status_label.setStyleSheet("color: #aaaaaa; font-style: italic;")
        else:
            self.status_label.setStyleSheet("color: #6c757d; font-style: italic;")    
    def cleanup_after_calculation(self):
        """计算完成后清理输入框并恢复按钮状态"""
        self.input_field.clear()
        self.calculate_btn.setEnabled(True)
        self.input_field.setFocus()
        
        # 停止加载动画
        self.stop_loading_animation()
    
    
    def show_error(self, error_msg):
        self.result_display.setPlainText(f"错误: {error_msg}")
        self.status_label.setText("发生错误")
        self.stop_loading_animation()

        # 清空存储的成功结果，因为这次出错了
        self._last_target = None
        self._last_expression = None
        self._last_elapsed_time = None

    def closeEvent(self, event):
        # 重写关闭事件，最小化到托盘
        self.hide()
        self.tray_icon.show()
        event.ignore()
        
    def show_normal(self):
        # 从托盘恢复窗口
        self.show()
        self.tray_icon.hide()
        
    def on_tray_icon_activated(self, reason):
        # 处理托盘图标点击事件
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_normal()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序字体
    font = QFont()
    font.setFamily("Microsoft YaHei" if sys.platform == "win32" else "PingFang SC")
    app.setFont(font)
    
    window = NineSolverGUI()
    window.show()
    sys.exit(app.exec())