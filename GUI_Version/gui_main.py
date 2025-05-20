# gui_main.py
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QSizePolicy, 
                             QSystemTrayIcon, QMenu, QGraphicsBlurEffect)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QEvent, QRect, QParallelAnimationGroup, QSize, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QPalette, QImage, QTextCursor

from main import ImprovedNineExpressionFinder
from Icon_Data import ICON_DATA
from setting_grey import SETTING_GREY
from setting_green import SETTING_GREEN
from widgets import CustomSwitch
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

LIGHT_STYLESHEET_BASE_COLORS = {
    "label_color": "#495057",
    "button_bg": "#4a90e2", # 这是计算按钮的颜色
}
DARK_STYLESHEET_ACTIVE_BASE_COLORS = {
    "main_frame_bg": "#2a3542", # 这是设置页面的深色激活背景
    "label_color": "#b0c4de",
    "button_bg": "#4682b4", # 这是计算按钮的颜色
}
DARK_STYLESHEET_INACTIVE_BASE_COLORS = {
    "main_frame_bg": "#262e38", # 这是设置页面的深色非激活背景 (如果需要区分)
                                # 或者直接用 #2a3542，让它不随主窗口激活状态变
    "label_color": "#9098a3",
    "button_bg": "#3e688f", # 这是计算按钮的颜色
}

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
            # 获取按钮当前的几何形状作为动画的基准
            current_geometry = self.geometry() 

            # 按下动画：按钮向下微移
            # 创建当前几何形状的副本进行修改
            pressed_geometry = QRect(current_geometry) 
            pressed_geometry.translate(0, 2) # 向下移动2像素 (你可以调整这个 '2' 值)
                                             # 例如，用 1 会更细微，用 3 会更明显

            # 设置按下动画的起止值
            self.press_anim.setStartValue(current_geometry)
            self.press_anim.setEndValue(pressed_geometry)
            
            # 设置释放动画的起止值
            self.release_anim.setStartValue(pressed_geometry)
            self.release_anim.setEndValue(current_geometry) # 恢复到动画开始前的几何形状
            
            # 启动动画组
            self.animation_group.start()
            
    def mousePressEvent(self, event):
        self.triggerAnimation()
        super().mousePressEvent(event)
        
    def resizeEvent(self, event: QEvent): 
        super().resizeEvent(event)
        # 如果窗口大小调整可能影响 settings_button 的大小（虽然现在是固定的）
        # 或者影响其在布局中的相对位置，进而影响 mapToGlobal
        if hasattr(self, 'settings_button') and hasattr(self, 'left_placeholder'):
            # 如果 settings_button 的宽度是动态的，这里需要更新
            # self.left_placeholder.setFixedWidth(self.settings_button.width())
            pass # 当前 settings_button 大小固定，init_ui 时已设置 left_placeholder

        # 同步克oned按钮的位置
        # 只有当设置页面关闭（即原始按钮应该可见）或克隆按钮当前可见时才同步
        if (hasattr(self, 'settings_button') and self.settings_button.isVisible()) or \
           (hasattr(self, 'cloned_settings_button') and self.cloned_settings_button.isVisible()):
            if hasattr(self, '_synchronize_cloned_button_position'):
                 QTimer.singleShot(0, self._synchronize_cloned_button_position) # 延迟一点确保布局更新

    def _synchronize_cloned_button(self):
        """将克隆按钮的属性（大小、图标、位置）与原始按钮同步。"""
        if not hasattr(self, 'settings_button') or not hasattr(self, 'cloned_settings_button'):
            return

        # 同步大小和IconSize (图标本身由 _update_cloned_button_style 设置)
        self.cloned_settings_button.setFixedSize(self.settings_button.size())
        self.cloned_settings_button.setIconSize(self.settings_button.iconSize())
        
        self._synchronize_cloned_button_position() # 调用位置同步
        self._update_cloned_button_style() # 确保图标也同步
        
        if self.cloned_settings_button.isVisible(): # 如果克隆按钮应该可见，则确保它在顶层
            self.cloned_settings_button.raise_()

   # _synchronize_cloned_button 方法也应调用 _synchronize_cloned_button_position
    # 或者将位置同步逻辑完全放在 _synchronize_cloned_button_position 中，
    # 而 _synchronize_cloned_button 负责大小和图标。
    # 我修改一下 _synchronize_cloned_button：
    def _synchronize_cloned_button(self):
        """将克隆按钮的属性（大小、图标、位置）与原始按钮同步。"""
        if not hasattr(self, 'settings_button') or not hasattr(self, 'cloned_settings_button'):
            return

        self.cloned_settings_button.setFixedSize(self.settings_button.size())
        self.cloned_settings_button.setIconSize(self.settings_button.iconSize())
        # 图标由 _update_cloned_button_style 处理
        
        self._synchronize_cloned_button_position() # 调用位置同步
        self.cloned_settings_button.raise_()                  

class SettingsPage(QWidget):
    closed = pyqtSignal() # 定义一个关闭信号
    hide_animation_started = pyqtSignal() # 定义隐藏动画开始信号
    accumulate_setting_changed = pyqtSignal(bool)
    def __init__(self, parent=None, initial_accumulate_state=False):
        super().__init__(parent)
        self.setObjectName("settingsPage")
        # 设置为无边框窗口部件，并且在父部件之上（如果希望它覆盖其他内容）
        # 但我们将其作为子部件添加，并用动画控制其显示和位置
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20) # 内边距
        layout.setSpacing(15)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)  # 关键！确保样式表背景生效
        self.update()  # 立即触发重绘   
        self.setAutoFillBackground(True)  # 启用自动填充背景

        self.title_label = QLabel("设置")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # ---- 新增：数据累积开关 ----
        switch_layout = QHBoxLayout()
        switch_layout.setSpacing(10)
        
        self.accumulate_label = QLabel("累积计算结果:")
        switch_layout.addWidget(self.accumulate_label)
        
        self.accumulate_switch = CustomSwitch(self)
        self.accumulate_switch.setChecked(initial_accumulate_state) # 设置初始状态
        self.accumulate_switch.toggled.connect(self.on_accumulate_switch_changed)
        switch_layout.addWidget(self.accumulate_switch, 0, Qt.AlignmentFlag.AlignLeft) # 让开关靠左，标签占据剩余空间
        switch_layout.addStretch(1) # 将开关推向左边

        layout.addLayout(switch_layout)
        # ------------------------------

        self.placeholder_label = QLabel("")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # 你之前的代码这里可能漏了
        self.placeholder_label.setWordWrap(True) # 你之前的代码这里可能漏了
        layout.addWidget(self.placeholder_label, 1)

        # 关闭按钮
        self.close_button = QPushButton("关闭")
        self.close_button.setObjectName("settingsCloseButton")
        self.close_button.clicked.connect(self.hide_animated) # 连接到隐藏动画
        layout.addWidget(self.close_button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.hide() # 默认隐藏

        # 动画相关
        self.animation = QPropertyAnimation(self, b"geometry")
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity") # 改为 windowOpacity
        self.animation_group = QSequentialAnimationGroup(self) # 改为并行，或根据需要调整
                                                            # 使用 QParallelAnimationGroup 可能更适合同时缩放和淡化
        self.parallel_anim_group = QParallelAnimationGroup(self)
        self.parallel_anim_group.addAnimation(self.animation)
        self.parallel_anim_group.addAnimation(self.opacity_animation)

    def on_accumulate_switch_changed(self, checked):
        """当开关状态改变时，发出信号。"""
        self.accumulate_setting_changed.emit(checked)

    # ---- 新增：一个方法来从外部设置开关状态 (如果需要的话) ----
    def set_accumulate_switch_state(self, checked):
        self.accumulate_switch.setChecked(checked)
    def show_animated(self):
        if not self.parentWidget():
            return

        parent_rect = self.parentWidget().rect()
        # 目标尺寸 (例如父窗口的 70%)
        target_width = int(parent_rect.width() * 0.7)
        target_height = int(parent_rect.height() * 0.6)
        target_x = parent_rect.center().x() - target_width // 2
        target_y = parent_rect.center().y() - target_height // 2
        
        # 起始尺寸和位置 (中心点，非常小)
        start_x = parent_rect.center().x()
        start_y = parent_rect.center().y()
        
        self.setGeometry(start_x, start_y, 0, 0) # 初始在中心，大小为0
        self.setWindowOpacity(0.0) # 初始完全透明
        self.show()
        self.raise_() # 确保在最上层

        self.animation.setDuration(300)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(target_x, target_y, target_width, target_height))
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.opacity_animation.setDuration(250) # 淡入稍快一点
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.Linear)

        self.parallel_anim_group.start()
        
    def hide_animated(self):
        self.hide_animation_started.emit()
        
        if not self.parentWidget():
            self.hide()
            self.closed.emit()
            return

        parent_rect = self.parentWidget().rect()
        current_geometry = self.geometry()

        # 结束尺寸和位置 (回到中心点，非常小)
        end_x = parent_rect.center().x()
        end_y = parent_rect.center().y()

        self.animation.setDuration(250)
        self.animation.setStartValue(current_geometry)
        self.animation.setEndValue(QRect(end_x, end_y, 0, 0))
        self.animation.setEasingCurve(QEasingCurve.Type.InQuad)

        self.opacity_animation.setDuration(300) # 淡出稍慢
        self.opacity_animation.setStartValue(self.windowOpacity())
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.Linear)
        
        # 确保动画结束后隐藏并发出信号
        # QAbstractAnimation.finished信号在动画组完成时发出
        if self.parallel_anim_group.state() == QParallelAnimationGroup.State.Running:
             self.parallel_anim_group.stop() # 停止可能正在进行的动画

        # 重新连接 finished 信号以避免多次连接
        try:
            self.parallel_anim_group.finished.disconnect(self._on_hide_anim_finished)
        except TypeError: # 如果之前没有连接过
            pass
        self.parallel_anim_group.finished.connect(self._on_hide_anim_finished)
        
        self.parallel_anim_group.start()

    def _on_hide_anim_finished(self):
        self.hide()
        self.closed.emit()
        # 断开连接，避免下次 show 时再次触发
        try:
            self.parallel_anim_group.finished.disconnect(self._on_hide_anim_finished)
        except TypeError:
            pass

    def update_theme_styling(self, main_window_theme, is_main_window_active):
        bg_color = ""
        text_color = ""
        button_bg_color = ""
        button_text_color = "white"

        if main_window_theme == "dark":
            bg_color = "#2a3542"  # 深色设置界面固定背景色
            # 文本和按钮颜色仍然可以根据主窗口激活状态调整，以保持视觉一致性
            text_color = DARK_STYLESHEET_ACTIVE_BASE_COLORS["label_color"] if is_main_window_active else DARK_STYLESHEET_INACTIVE_BASE_COLORS["label_color"]
            button_bg_color = DARK_STYLESHEET_ACTIVE_BASE_COLORS["button_bg"] if is_main_window_active else DARK_STYLESHEET_INACTIVE_BASE_COLORS["button_bg"]
        else: # light
            bg_color = "#ffffff" # 浅色的设置界面是白色
            text_color = LIGHT_STYLESHEET_BASE_COLORS["label_color"]
            button_bg_color = LIGHT_STYLESHEET_BASE_COLORS["button_bg"]

        self.setStyleSheet(f"""
            #settingsPage {{
                background-color: {bg_color};
                border-radius: 8px; /* 给设置页面一些圆角 */
                border: 1px solid {QColor(bg_color).darker(120).name()}; /* 边框比背景稍暗 */
            }}
            #settingsPage QLabel {{ /* 应用于设置页面内的所有 QLabel */
                color: {text_color};
            }}
            #settingsPage QPushButton#settingsCloseButton {{ /* 特定于关闭按钮 */
                background-color: {button_bg_color};
                color: {button_text_color};
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 60px;
                max-width: 80px; /* 与计算按钮一致 */
            }}
            #settingsPage QPushButton#settingsCloseButton:hover {{
                background-color: {QColor(button_bg_color).darker(115).name()};
            }}
        """)
        self.title_label.setStyleSheet(f"color: {text_color};") # 确保标题颜色也更新

# 为了方便 SettingsPage 访问主题颜色，我们可以将颜色提取出来
# (或者 SettingsPage 在更新时从父窗口获取这些颜色)
# 这里我先假设我们将颜色值硬编码或通过参数传递

# 在全局范围定义这些，或者作为 NineSolverGUI 的类属性
LIGHT_STYLESHEET_BASE_COLORS = {
    "label_color": "#495057",
    "button_bg": "#4a90e2",
}
DARK_STYLESHEET_ACTIVE_BASE_COLORS = {
    "main_frame_bg": "#2a3542",
    "label_color": "#b0c4de",
    "button_bg": "#4682b4",
}
DARK_STYLESHEET_INACTIVE_BASE_COLORS = {
    "main_frame_bg": "#262e38",
    "label_color": "#9098a3",
    "button_bg": "#3e688f",
}

class NineSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()       
        self.current_theme = get_system_theme() # 获取初始系统主题
        self._theme_initialized = False # 添加一个标志位        
        self.accumulate_results = False # 新增：用于控制是否累积结果
        # 初始化系统托盘
        self.tray_icon = QSystemTrayIcon(self)
        self.ICON_DATA = ICON_DATA 

        # 新增：存储所有成功计算的结果
        self.historical_results = []
        self.tray_icon.setIcon(QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(self.ICON_DATA)))))
        
        # 新增：预加载设置图标
        self.setting_icon_light = QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(SETTING_GREY))))
        self.setting_icon_dark = QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(SETTING_GREEN))))

        # 初始化模糊效果
        self.blur_effect = QGraphicsBlurEffect(self) # 父对象可以是 self
        self.blur_effect.setBlurRadius(0)  # 设置模糊半径，可以调整
        self.blur_effect.setEnabled(False) # 默认不启用

        # 初始化模糊动画
        self.blur_animation = QPropertyAnimation(self.blur_effect, b"blurRadius") # <--- 新增
        # 动画时长可以和设置页面的动画时长协调
        # SettingsPage 的动画时长是 300ms (show_animated) 和 250ms (hide_animated for geometry)
        # 我们可以选择一个相近的值，比如 300ms
        self.blur_animation.setDuration(300) # <--- 新增：动画持续时间
        self.blur_animation.setEasingCurve(QEasingCurve.Type.OutQuad) # <--- 新增：缓动曲线，与设置页面展开类似


        # 实例化设置页面，父对象是主窗口的 centralWidget，或者直接是主窗口
        # 如果父对象是 centralWidget，那么设置页面的坐标就是相对于 centralWidget 的
        # 如果父对象是 self (QMainWindow)，坐标是相对于 QMainWindow 的
        # 为了简单起见，先让父对象是 self，我们将在动画中计算相对于主窗口的坐标
        self.settings_page = SettingsPage(self) # 父对象设为 self
        self.settings_page.closed.connect(self.on_settings_page_fully_closed)
        self.settings_page.hide_animation_started.connect(self.on_settings_hide_anim_started) # <--- 新增：连接新信号

        self.settings_page.accumulate_setting_changed.connect(self.on_accumulate_setting_changed)
        # ---- 新增：创建克隆齿轮按钮 ----
        self.cloned_settings_button = QPushButton(self) # 父对象是主窗口 self
        self.cloned_settings_button.setObjectName("clonedSettingsButton")
        # 外观属性将在 init_ui 后，根据原始按钮设置，并由 _update_cloned_button_style 更新
        self.cloned_settings_button.setFlat(True)
        self.cloned_settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cloned_settings_button.hide() # 默认隐藏
        self.cloned_settings_button.clicked.connect(self.toggle_settings_page) # 点击也触发toggle


        # 创建托盘菜单
        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示   ")
        show_action.triggered.connect(self.show_normal)
        quit_action = tray_menu.addAction("退出   ")
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

    def on_accumulate_setting_changed(self, checked):
        self.accumulate_results = checked
        print(f"Accumulate results setting changed to: {self.accumulate_results}")
        
        if not self.accumulate_results: 
            # 当从累积变为不累积时：
            last_valid_result = None
            # 查找最后一个有效的（非错误）结果以保留显示
            for entry in reversed(self.historical_results):
                if entry['type'] == 'success' or entry['type'] == 'not_found':
                    last_valid_result = entry
                    break
            
            self.result_display.clear() 
            self.historical_results = [] # 清空历史记录

            if last_valid_result:
                self.historical_results.append(last_valid_result) # 只保留最后一个有效结果
                self._render_all_historical_results() # 重新渲染这一个
            # else: 历史中没有有效结果，保持空白
    def _synchronize_cloned_button(self):
        """将克隆按钮的属性（大小、图标）与原始按钮同步，并设置其初始位置。"""
        if not hasattr(self, 'settings_button') or not hasattr(self, 'cloned_settings_button'):
            return

        # 同步大小
        self.cloned_settings_button.setFixedSize(self.settings_button.size())
        self.cloned_settings_button.setIconSize(self.settings_button.iconSize())

        # 同步图标 (通过 _update_cloned_button_style 来处理更佳，因为它依赖主题)
        # self._update_cloned_button_style() # 确保调用它来设置正确的初始图标

        # 计算原始按钮在主窗口中的绝对位置
        # 需要确保 self.settings_button 已经有正确的几何形状
        # 这通常在窗口显示后才最准确，但我们可以在 init_ui 后尝试获取
        # 如果在 init_ui 后立即获取位置不准，可能需要延迟到 showEvent 或第一次 resizeEvent
        original_button_global_pos = self.settings_button.mapToGlobal(self.settings_button.rect().topLeft())
        cloned_button_pos_in_main_window = self.mapFromGlobal(original_button_global_pos)
        self.cloned_settings_button.move(cloned_button_pos_in_main_window)
        
        # 确保克隆按钮在最上层 (相对于主窗口内的其他非顶层子部件)
        self.cloned_settings_button.raise_()    
    def toggle_settings_page(self):
        # 检查设置页面动画和模糊动画状态
        settings_page_anim_running = self.settings_page.parallel_anim_group.state() == QParallelAnimationGroup.State.Running
        blur_anim_running = self.blur_animation.state() == QPropertyAnimation.State.Running

        # 移除 cloned_button_anim_running 的检查，因为它不再有动画
        if settings_page_anim_running or blur_anim_running:
            print("Animation in progress, ignoring toggle request.")
            return

        target_blur_radius = 10
        animation_duration = 300 
        # button_fade_duration = 200 # 不再需要

        # 移除 self.cloned_button_fade_animation.setDuration(button_fade_duration)

        if self.settings_page.isVisible():
            print("Toggle: Settings page is visible, hiding it (triggered by cloned_button or direct call).")
            # 只启动设置页面的隐藏动画。
            # settings_page.hide_animated() 会触发:
            # 1. self.settings_page.hide_animation_started -> self.on_settings_hide_anim_started (处理模糊消失动画)
            # 2. settings_page 动画结束后 -> self.settings_page.closed -> self.on_settings_page_fully_closed (处理按钮切换)
            self.settings_page.hide_animated() 
            
            # 克隆按钮保持可见，直到 on_settings_page_fully_closed 中处理
            # 原始按钮保持隐藏，直到 on_settings_page_fully_closed 中处理

        else: # Settings page is hidden, show it
            print("Toggle: Settings page is hidden, showing it.")
            # ---- 新增：确保设置页面的开关状态与当前设置同步 ----
            if hasattr(self.settings_page, 'set_accumulate_switch_state'):
                self.settings_page.set_accumulate_switch_state(self.accumulate_results)
            self._synchronize_cloned_button() 

            self.settings_button.setVisible(False)
            if hasattr(self, 'left_placeholder'):
                self.left_placeholder.setVisible(False) 

            self.cloned_settings_button.show()
            self.cloned_settings_button.raise_() 
            # 移除 self.cloned_button_fade_animation 的启动代码
            # 如果之前设置了 opacity effect，现在没有动画了，确保它是完全可见的
            if hasattr(self, 'cloned_button_opacity_effect'):
                 self.cloned_button_opacity_effect.setOpacity(1.0)


            self.settings_page.update_theme_styling(self.current_theme, self.isActiveWindow())

            if hasattr(self, 'blur_effect'):
                self.blur_effect.setEnabled(True)
                self.blur_animation.stop()
                self.blur_animation.setDuration(animation_duration)
                self.blur_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
                self.blur_animation.setStartValue(self.blur_effect.blurRadius())
                self.blur_animation.setEndValue(target_blur_radius)
                self.blur_animation.start()
            
            self.settings_page.show_animated()   
   
   # 新增槽函数：当设置页面开始隐藏动画时调用
    def on_settings_hide_anim_started(self):
        print("Settings hide animation started, starting blur removal animation.") # 调试用
        animation_duration_hide = 300 # 与 SettingsPage 的 hide_animated 的 opacity 动画时长一致 (或者 geometry 的 250ms)
                                    # 保持和展开时一致的 300ms 可能更协调

        if hasattr(self, 'blur_effect') and hasattr(self, 'blur_animation'):
            self.blur_animation.stop() 
            self.blur_animation.setDuration(animation_duration_hide)
            self.blur_animation.setEasingCurve(QEasingCurve.Type.InQuad) 
            self.blur_animation.setStartValue(self.blur_effect.blurRadius()) 
            self.blur_animation.setEndValue(0) 

            try:
                self.blur_animation.finished.disconnect(self._on_blur_anim_finished_disable_effect)
            except TypeError:
                pass 
            self.blur_animation.finished.connect(self._on_blur_anim_finished_disable_effect)
            
            self.blur_animation.start()
        else: 
            if hasattr(self, 'blur_effect'):
                self.blur_effect.setEnabled(False)
    
    def _update_cloned_button_style(self):
        """根据当前主题更新克隆设置按钮的图标。"""
        if not hasattr(self, 'current_theme') or not self._theme_initialized:
            return
        if not hasattr(self, 'setting_icon_light') or not hasattr(self, 'setting_icon_dark'):
            return
        if not hasattr(self, 'cloned_settings_button'): # 确保克隆按钮存在
            return

        current_icon = None
        if self.current_theme == "dark":
            current_icon = self.setting_icon_dark
        else: # light
            current_icon = self.setting_icon_light

        if current_icon:
            self.cloned_settings_button.setIcon(current_icon)
        
        # 克隆按钮也需要基本样式，确保透明无边框
        self.cloned_settings_button.setStyleSheet("""
            QPushButton#clonedSettingsButton {
                border: none;
                background-color: transparent;
                padding: 0px;
            }
            QPushButton#clonedSettingsButton:hover {
                /* 与原始按钮的 hover 效果一致或类似 */
                background-color: rgba(128, 128, 128, 20); 
            }
        """)

    def _update_settings_button_style(self):
        """根据当前主题更新设置按钮的图标和基本样式。"""
        # 确保主题和图标资源已初始化
        if not hasattr(self, 'current_theme') or not self._theme_initialized:
            return # 如果主题未初始化，则不执行任何操作
        if not hasattr(self, 'setting_icon_light') or not hasattr(self, 'setting_icon_dark'):
            print("警告: _update_settings_button_style 中设置图标尚未加载。")
            return

        current_icon = None
        if self.current_theme == "dark":
            current_icon = self.setting_icon_dark # 深色模式使用 SETTING_GREEN (你命名的绿色图标)
        else: # light
            current_icon = self.setting_icon_light # 浅色模式使用 SETTING_GREY (你命名的灰色图标)

        if current_icon:
            self.settings_button.setIcon(current_icon)
        
        # 为按钮应用基本样式，确保其透明无边框
        self.settings_button.setStyleSheet("""
            QPushButton#settingsButton {
                min-width: 32px;    /* 强制最小宽度 */
                min-height: 32px;   /* 强制最小高度 */
                max-width: 32px;    /* 限制最大宽度 */
                max-height: 32px;   /* 限制最大高度 */
                border: none;                   /* 确保无边框 */
                background-color: transparent;  /* 确保背景透明 */
                padding: 0px;                   /* 通常 flat 按钮不需要内边距 */

            }
            QPushButton#settingsButton:hover {
                background-color: rgba(128, 128, 128, 20); 
                 /* 半透明灰色 */
            }
        """)
        if hasattr(self, 'cloned_settings_button') and self.cloned_settings_button.isVisible():
             self._update_cloned_button_style()

    def _on_blur_anim_finished_disable_effect(self):
        if hasattr(self, 'blur_effect'):
            # 检查最终的 blurRadius，确保它确实是0才禁用
            if self.blur_effect.blurRadius() < 0.1: # 浮点数比较，用一个小阈值
                self.blur_effect.setEnabled(False)
        # 断开信号，避免下次动画时重复执行或错误的上下文
        try:
            self.blur_animation.finished.disconnect(self._on_blur_anim_finished_disable_effect)
        except TypeError:
            pass
    def on_settings_page_fully_closed(self): 
        print("on_settings_page_fully_closed: Settings page animation finished.")
        
        # 此处是设置页面几何和透明度动画完成的时间点。
        # 模糊消失动画可能仍在进行或刚刚完成（通过 on_settings_hide_anim_started 触发）。
        # 我们现在可以安全地切换按钮了。

        if hasattr(self, 'cloned_settings_button') and self.cloned_settings_button.isVisible():
            print("Hiding cloned_settings_button, showing original settings_button.")
            self.cloned_settings_button.hide()
            # 重置克隆按钮的透明度（如果之前用了opacity effect但现在没动画了，也无妨）
            if hasattr(self, 'cloned_button_opacity_effect'): 
                 self.cloned_button_opacity_effect.setOpacity(1.0) 

        if hasattr(self, 'settings_button') and not self.settings_button.isVisible():
            self.settings_button.setVisible(True)
        if hasattr(self, 'left_placeholder') and not self.left_placeholder.isVisible():
            self.left_placeholder.setVisible(True)
        
        # 确保原始按钮的样式是最新的（例如，如果窗口激活状态在设置页面显示期间改变了）
        if hasattr(self, '_update_settings_button_style'):
            self._update_settings_button_style() 
        
        # 注意：模糊效果的 setEnabled(False) 是由 _on_blur_anim_finished_disable_effect 单独处理的，
        # 它会在模糊动画完成后执行。这个时序通常可以接受。  
    def showEvent(self, event_obj: QEvent):
        """窗口第一次显示时，应用完整的主题并强制使用激活样式。"""
        super().showEvent(event_obj) 
        if not self._theme_initialized: # 使用你已有的标志位 _theme_initialized
            print("showEvent: Applying initial theme (forcing active style).")
            self.apply_theme_styling(self.current_theme, force_active_on_initial_show=True) 
            #self._theme_initialized = True
        
        # 使用 QTimer.singleShot 确保在当前事件处理完成后执行，此时布局更稳定
        if hasattr(self, '_synchronize_cloned_button'): # 确保方法存在
             QTimer.singleShot(0, self._synchronize_cloned_button)

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
        print(f"_update_activation_styles: Active: {is_active}. Current theme: {self.current_theme}")
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

        self._update_settings_button_style()
        self._update_cloned_button_style()
        
        self.settings_page.update_theme_styling(self.current_theme, is_active)
        #self.update()
    
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
        
        # 1. 更新当前主题记录
        self.current_theme = theme_name
        
        # 如果是首次强制应用 (通常来自 showEvent), 并且主题尚未标记为已初始化，
        # 则在此处标记，以确保后续依赖 _theme_initialized 的更新（如按钮图标）能正确执行。
        if force_active_on_initial_show and not self._theme_initialized:
            print("apply_theme_styling: Setting _theme_initialized = True for initial load.") # 调试用，可以删除
            self._theme_initialized = True  # <--- 在这里设置 
        
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

        self._update_settings_button_style()
        self._update_cloned_button_style()
        
        # 5. 其他更新
        self.stop_loading_animation()
        self.update() # 通常 setStyleSheet 会处理这个，但为了确保，我们也可以显式调用
        # ---- 修改：根据累积模式决定如何渲染 ----
        if self.accumulate_results and self.historical_results:
            self._render_all_historical_results() # 重绘所有历史记录
        elif not self.accumulate_results and self.historical_results: # 非累积，但有"最后"一个结果
            #  _render_all_historical_results 也能处理只渲染一个的情况 (如果列表只有一个元素)
             self._render_all_historical_results()
        elif not self.historical_results: # 没有任何结果可显示
            self.result_display.clear()
        self.settings_page.update_theme_styling(self.current_theme, self.isActiveWindow())

    def init_ui(self):
        self.main_central_widget = QWidget() 
        self.setCentralWidget(self.main_central_widget) 
        main_layout = QVBoxLayout(self.main_central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15) # 统一间距

        # 1. 创建 QLabel 实例 (self.title_label, self.description)
        self.title_label = QLabel("⑨ 表达式求解器")
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        # 颜色将由全局样式表 NineSolverGUI #title_label 控制

        self.description = QLabel("输入一个整数，琪露诺会尝试用9、99、999的加减乘除组合来表示它")
        self.description.setObjectName("description")
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 颜色将由全局样式表 NineSolverGUI #description 控制

        # 2. 创建设置按钮实例
        self.settings_button = QPushButton()
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setFixedSize(32, 32)
        self.settings_button.setIconSize(QSize(28, 28)) # <--- 新增：图标在按钮内的大小 (你可以调整)
        self.settings_button.setFlat(True) # <--- 新增：使按钮看起来更像一个图标
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor) # <--- 新增：设置鼠标悬停手势
        self.settings_button.clicked.connect(self.toggle_settings_page)

        # 3. 构建顶部栏布局 (包含标题和设置按钮)
        top_bar_layout = QHBoxLayout()
        # top_bar_layout.setContentsMargins(0,0,0,0) # 可选：如果希望布局更紧凑，可以移除或减少边距

        # 新增：左侧占位符，用于平衡右侧的设置按钮
        # self.settings_button 的宽度是 32px
        self.left_placeholder = QWidget()  # 创建一个空的QWidget作为占位符
        self.left_placeholder.setFixedWidth(self.settings_button.width()) # 设置其宽度与 settings_button 一致
        top_bar_layout.addWidget(self.left_placeholder) # 将占位符添加到布局的左侧

        # 标题标签，使其在中间的剩余空间伸展
        # self.title_label 已经设置了setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 所以它的文本会在它自己的区域内居中
        top_bar_layout.addWidget(self.title_label, 1) # 参数 1 表示它会占据所有可用的伸展空间

        # 设置按钮，保持在最右侧
        # self.settings_button.setFixedSize(32, 32) 已经设置了固定大小
        # Qt.AlignmentFlag.AlignRight 在这里其实不是必须的，因为 QHBoxLayout 按顺序排列
        # 但保留它也没有坏处，确保它在其“单元格”内靠右（如果单元格比它大的话）
        top_bar_layout.addWidget(self.settings_button, 0) # 参数 0 表示不伸展

        # 4. 将顶部栏和描述添加到主布局
        main_layout.addLayout(top_bar_layout)
        main_layout.addWidget(self.description) # 描述在标题栏下方，默认水平拉伸，垂直居中

        # 5. 主内容区域 Frame
        self.main_frame = QWidget()
        self.main_frame.setObjectName("main_frame")
        frame_layout = QVBoxLayout(self.main_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(20) # main_frame 内部的间距

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
        
        main_layout.addWidget(self.main_frame) # 将包含所有输入输出的 frame 添加到主布局

        # 将模糊效果应用到 centralWidget
    # 确保这是在 centralWidget 和它的子内容都创建之后
        if hasattr(self, 'blur_effect') and self.main_central_widget:
            self.main_central_widget.setGraphicsEffect(self.blur_effect)

        # 底部状态栏
        self.status_bar = self.statusBar()
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("status_label")
        self.status_bar.addPermanentWidget(self.status_label)
        
        self.input_field.returnPressed.connect(self.on_enter_pressed)

        # 在 init_ui 的末尾，或者 apply_theme_styling 第一次被调用时，
        # 更新 settings_button 的颜色
        self._update_settings_button_style()

        
    def show_result(self, target_str: str, expr_str: str, elapsed: float): # Renamed expr to expr_str
        self.stop_loading_animation()
        
        new_result_entry = {
            'target': target_str,
            'expr': expr_str,
            'elapsed': elapsed,
            'type': 'success' if expr_str else 'not_found' 
        }

        if self.accumulate_results:
            self.historical_results.append(new_result_entry)
            self._render_all_historical_results() # 渲染所有累积的结果
        else:
            # 非累积模式，只显示当前这一个 (可以临时存到historical_results[0]或单独变量)
            self.historical_results = [new_result_entry] # 或者用独立的 _last_... 变量
            self._render_all_historical_results() # 也可以调用它，它会清空并只渲染这一个

        if expr_str: 
            self.status_label.setText(f"计算完成 - 耗时 {elapsed:.2f}秒")
            finder = ImprovedNineExpressionFinder() 
            finder.play_baka_sound()
        else:
            self.status_label.setText("未找到结果")

    def on_enter_pressed(self):
        self.calculate_btn.triggerAnimation()
        self.calculate_btn.click()
        
    def setup_animations(self):
        # 状态栏加载动画
        self.loading_animation = QPropertyAnimation(self.status_label, b"styleSheet")
        self.loading_animation.setDuration(500)
        self.loading_timer = self.startTimer(500)  # 每500ms切换一次状态
        self.loading_state = 0
        
    def on_worker_error(self, error_msg: str):
        """
        处理来自 WorkerThread 的错误信号。
        将错误信息添加到历史记录并更新显示。
        """
        print(f"WorkerThread error: {error_msg}")

        error_entry = {
            'type': 'error',
            'message': error_msg
            # 如果 WorkerThread 的 error_occurred 信号也发送了 target，可以在这里添加
            # 'target': target_from_signal 
        }

        if self.accumulate_results:
            self.historical_results.append(error_entry)
        else:
            # 非累积模式，错误会覆盖之前的内容
            self.historical_results = [error_entry] 
        
        self._render_all_historical_results() # 使用新的渲染方法

        self.status_label.setText("计算发生错误") # 或者更具体的错误提示
        self.stop_loading_animation()
        
        # 确保按钮在出错时恢复可用 (cleanup_after_calculation 也会做这个，但这里再做一次也无妨)
        if hasattr(self, 'calculate_btn') and not self.calculate_btn.isEnabled():
            self.calculate_btn.setEnabled(True)    
    
    def start_calculation(self):
        # 不再单独管理 _last_target 等，它们会作为新条目进入 historical_results
        
        if not self.accumulate_results:
            self.result_display.clear()
            self.historical_results = [] # <--- 清空历史记录
            
        input_text = self.input_field.text().strip()
        
        # ... (quit logic) ...
            
        try:
            target_value = 0 
            if not input_text: 
                raise ValueError("输入不能为空") 

            if 'e' in input_text.lower():
                target_value = int(float(input_text)) 
            else:
                target_value = int(input_text)
            
            self.calculate_btn.setEnabled(False)
            
            # "计算中..." 的提示处理
            if not self.accumulate_results:
                self.result_display.setPlainText("计算中，请稍候...")
            else:
                # 累积模式下，我们不显示“计算中”，因为会覆盖历史。
                # 用户会看到旧内容，直到新结果追加。
                pass
                
            self.status_label.setText("正在计算...")
            self.start_loading_animation()
            
            # 记录当前正在尝试计算的目标，以便出错时可以引用 (可选)
            # self._currently_calculating_target = str(target_value) 

            self.worker = WorkerThread(target_value)
            self.worker.result_ready.connect(self.show_result)
            self.worker.error_occurred.connect(self.on_worker_error) # <--- 改用新槽函数
            self.worker.finished.connect(self.cleanup_after_calculation)
            self.worker.start()
            
        except ValueError as e: 
            print(f"ValueError during input parsing: {e}")
            # 将输入解析错误也记录到历史（如果需要）
            error_entry = {
                'type': 'error',
                'message': f"输入无效"
            }
            if self.accumulate_results:
                self.historical_results.append(error_entry)
            else:
                self.historical_results = [error_entry]
            self._render_all_historical_results() # 显示错误

            self.status_label.setText("输入错误")
            self.input_field.clear() 
            if self.input_field.placeholderText() != "":
                self.input_field.setPlaceholderText("")
            if hasattr(self, 'calculate_btn'):
                self.calculate_btn.setEnabled(True)
    
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
        if self.input_field.placeholderText() != "": # 检查是否已有占位符，避免不必要的设置
            self.input_field.setPlaceholderText("") 
        self.calculate_btn.setEnabled(True)
        self.input_field.setFocus()
        
        # 停止加载动画
        self.stop_loading_animation()

    def _render_all_historical_results(self):
        """
        清空结果显示区域，并根据 self.historical_results 中的所有条目
        和当前主题重新渲染内容。
        """
        self.result_display.clear()
        
        # --- 获取当前主题颜色 ---
        unified_dark_text_color = ""
        light_text_color_default = "#212529" 
        light_text_color_time = "#6c757d"   
        light_text_color_expr_color = "#000000" 

        if self.current_theme == "dark":
            if self.isActiveWindow(): unified_dark_text_color = "#b0c4de" 
            else: unified_dark_text_color = "#a0abb3" 
            html_default_text_color = unified_dark_text_color
            time_color = unified_dark_text_color
            expr_html_color = unified_dark_text_color 
        else: 
            html_default_text_color = light_text_color_default 
            time_color = light_text_color_time
            expr_html_color = light_text_color_expr_color 
        baka_color = "#2c9fff" if self.current_theme == "dark" else "#0165cc"
        # hr_color 和 visual_separator_html 已被移除
        error_html_color = '#ff6b6b' if self.current_theme == 'dark' else '#d9534f'
        # --- 颜色逻辑结束 ---

        for index, entry in enumerate(self.historical_results):
            entry_inner_html = ""

            if entry['type'] == 'success' or entry['type'] == 'not_found':
                target_str = entry['target']
                expr_str = entry.get('expr') 
                elapsed = entry.get('elapsed', 0.0)

                if expr_str: # 成功找到表达式
                    entry_inner_html = f"""
                        <p>目标: <span style="font-weight: bold;">{target_str}</span></p>
                        <p>结果 (<span style="color: {time_color};">{elapsed:.2f}秒</span>):</p>
                        <p><span style="font-weight: bold;">{target_str}</span> = <span style="color: {expr_html_color};">{expr_str}</span></p>
                        <p style="color: {baka_color}; font-weight: bold;">baka~<br><br><br></p>
                    """
                else: # 未找到表达式
                    entry_inner_html = f"""
                        <p>目标: <span style="font-weight: bold;">{target_str}</span></p>
                        <p>无法找到 {target_str} 的有效表达式</p>
                    """
            elif entry['type'] == 'error':
                message = entry['message']
                entry_inner_html = f"""
                     <p style="color: {error_html_color};">错误: {message}</p>
                """

            if entry_inner_html: 
                full_entry_html = f"""
                    <div style="font-family: Consolas, 'Courier New', monospace; font-size: 14px; color: {html_default_text_color};">
                        {entry_inner_html}
                    </div>
                """
                
                # 确保在追加前光标在末尾 (对于 insertHtml 可能不是严格必须，但 setHtml 后是)
                self.result_display.moveCursor(QTextCursor.MoveOperation.End)
                self.result_display.insertHtml(full_entry_html)
                
                # ---- 在每个条目后添加一些额外的垂直间距（如果需要的话） ----
                # 这可以替代之前的 <hr> 分隔符，提供视觉分隔
                if self.accumulate_results and index < len(self.historical_results) - 1: # 如果不是最后一个条目
                    self.result_display.moveCursor(QTextCursor.MoveOperation.End)
                    self.result_display.insertHtml("<br>") # 添加一个或两个换行符作为间距
                

        self.result_display.moveCursor(QTextCursor.MoveOperation.End)
        self.result_display.ensureCursorVisible()
    
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