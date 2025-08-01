# gui_main.py
import sys
from decimal import Decimal, getcontext
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QSizePolicy, 
                             QMenu, QGraphicsBlurEffect, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QEvent, QRect, QParallelAnimationGroup, QSize, QTimer, QPoint, QAbstractAnimation 
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QPalette, QImage, QTextCursor, QPaintEvent, QScreen, QMouseEvent, QResizeEvent

from main import ImprovedNineExpressionFinder
from typing import Optional
from Icon_Data import ICON_DATA
from setting_grey import SETTING_GREY
from setting_green import SETTING_GREEN
from fumo import FUMO
from widgets import CustomSwitch
import time
import base64
import random

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
    QPushButton#clearResultsButton {
        background-color: #5dade2; /* 清爽蓝色 */
    }
    QPushButton#clearResultsButton:hover {
        background-color: #45b3e0; /* 深一点的清爽蓝色 */
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
        :color white; /* 文字保持白色 */
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
    QPushButton#clearResultsButton {
        background-color: #5d8aa8; /* 深色激活状态下的蓝色 */
    }
    QPushButton#clearResultsButton:hover {
        background-color: #4a7c9b; /* 深一点的深色激活蓝色 */
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
    QPushButton#clearResultsButton {
        background-color: #507d9c; /* 深色非激活状态下的蓝色 */
    }
    QPushButton#clearResultsButton:hover {
        background-color: #426a8a; /* 深一点的深色非激活蓝色 */
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
            

# gui_main.py

class AnimatedPushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation_group = QSequentialAnimationGroup(self)
        
        self.press_anim = QPropertyAnimation(self, b"geometry")
        self.press_anim.setDuration(80)
        self.press_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.release_anim = QPropertyAnimation(self, b"geometry")
        self.release_anim.setDuration(120)
        self.release_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        
        self.animation_group.addAnimation(self.press_anim)
        self.animation_group.addAnimation(self.release_anim)
        # self.original_geometry = self.geometry() # 由于动画基于实时几何，此行不再必需

    def triggerAnimation(self):
        if self.animation_group.state() != QPropertyAnimation.State.Running:
            current_geometry = self.geometry() 
            pressed_geometry = QRect(current_geometry) 
            pressed_geometry.translate(0, 2) 

            self.press_anim.setStartValue(current_geometry)
            self.press_anim.setEndValue(pressed_geometry)
            
            self.release_anim.setStartValue(pressed_geometry)
            self.release_anim.setEndValue(current_geometry) 
            
            self.animation_group.start()
            
    def mousePressEvent(self, event: QMouseEvent): # <--- 建议类型为 QMouseEvent
        self.triggerAnimation()
        super().mousePressEvent(event)
        
    # resizeEvent 可以移除，因为 original_geometry 不再关键
    # def resizeEvent(self, event: QResizeEvent): # <--- 建议类型为 QResizeEvent
    #     super().resizeEvent(event)
    #     # self.original_geometry = self.geometry() # 不再必需                  

class SettingsPage(QWidget):
    closed = pyqtSignal() # 定义一个关闭信号
    hide_animation_started = pyqtSignal() # 定义隐藏动画开始信号
    accumulate_setting_changed = pyqtSignal(bool)
    fumo_easter_egg_changed = pyqtSignal(bool)
    baka_audio_setting_changed = pyqtSignal(bool)
    def __init__(self, parent=None, initial_accumulate_state=False, 
                 initial_fumo_state=False, initial_baka_audio_state=True, 
                 fumo_icon_pixmap: QPixmap = None): 
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        
        main_settings_layout = QVBoxLayout(self) # 主垂直布局
        main_settings_layout.setContentsMargins(20, 20, 20, 20) 
        main_settings_layout.setSpacing(15) # 行间距

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)  
        self.update()  
        self.setAutoFillBackground(True)  

        self.title_label = QLabel("设置")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_settings_layout.addWidget(self.title_label)
        main_settings_layout.addSpacing(10) # 标题和第一个设置项之间的额外间距

        # ---- 设置项1：数据累积 ----
        setting_item_layout_1 = QHBoxLayout() # 每项设置使用一个水平布局
        setting_item_layout_1.setContentsMargins(0, 5, 0, 5) # 设置项的上下内边距

        self.accumulate_label = QLabel("允许累积计算结果")
        # ---- 新增/修改：为 accumulate_label 设置字体 ----
        accumulate_label_font = QFont()
        accumulate_label_font.setPointSize(11) # 例如，设置为11号字，你可以调整
        accumulate_label_font.setBold(True)    # 设置为加粗
        self.accumulate_label.setFont(accumulate_label_font)
        # 让标签占据一些空间，但不要无限扩展，给开关留出位置
        self.accumulate_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        setting_item_layout_1.addWidget(self.accumulate_label, 1) # 参数1使其可以伸展

        self.accumulate_switch = CustomSwitch(self)
        self.accumulate_switch.setChecked(initial_accumulate_state) 
        self.accumulate_switch.toggled.connect(self.on_accumulate_switch_changed)
        # 开关使用固定大小或Preferred，不伸展
        self.accumulate_switch.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed) 
        setting_item_layout_1.addWidget(self.accumulate_switch, 0, Qt.AlignmentFlag.AlignRight) # <--- 开关靠右对齐

        main_settings_layout.addLayout(setting_item_layout_1)

         # ---- 设置项2：Baka 声音开关 ----
        setting_item_layout_baka_audio = QHBoxLayout()
        setting_item_layout_baka_audio.setContentsMargins(0, 5, 0, 5)

        self.baka_audio_label = QLabel("播放Baka音效")
        baka_audio_label_font = QFont() # 与 accumulate_label 字体一致
        baka_audio_label_font.setPointSize(11)
        baka_audio_label_font.setBold(True)
        self.baka_audio_label.setFont(baka_audio_label_font)
        self.baka_audio_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        setting_item_layout_baka_audio.addWidget(self.baka_audio_label, 1)

        self.baka_audio_switch = CustomSwitch(self)
        self.baka_audio_switch.setChecked(initial_baka_audio_state) # 设置初始状态
        self.baka_audio_switch.toggled.connect(self.on_baka_audio_switch_changed)
        self.baka_audio_switch.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        setting_item_layout_baka_audio.addWidget(self.baka_audio_switch, 0, Qt.AlignmentFlag.AlignRight)

        main_settings_layout.addLayout(setting_item_layout_baka_audio)
        # -----------------------------
        
        setting_item_layout_fumo = QHBoxLayout() # 重命名布局变量以避免冲突
        setting_item_layout_fumo.setContentsMargins(0, 5, 0, 5)

        self.fumo_icon_label = QLabel(self) 
        if fumo_icon_pixmap and not fumo_icon_pixmap.isNull():
            icon_size = 24 
            self.fumo_icon_label.setPixmap(fumo_icon_pixmap.scaled(
                icon_size, icon_size, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.fumo_icon_label.setText("Fumo:") 
            fumo_label_font = QFont() 
            fumo_label_font.setPointSize(11)
            fumo_label_font.setBold(True)
            self.fumo_icon_label.setFont(fumo_label_font)

        self.fumo_icon_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        setting_item_layout_fumo.addWidget(self.fumo_icon_label, 1)

        self.fumo_switch = CustomSwitch(self)
        self.fumo_switch.setChecked(initial_fumo_state)
        self.fumo_switch.toggled.connect(self.on_fumo_switch_changed)
        self.fumo_switch.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        setting_item_layout_fumo.addWidget(self.fumo_switch, 0, Qt.AlignmentFlag.AlignRight)

        main_settings_layout.addLayout(setting_item_layout_fumo)

        self.placeholder_label = QLabel("") # 或者保留一个空的，如果以后想显示动态内容
        self.placeholder_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_settings_layout.addWidget(self.placeholder_label, 1) # 让它占据剩余垂直空间


        self.close_button = QPushButton("关闭")
        self.close_button.setObjectName("settingsCloseButton")
        self.close_button.clicked.connect(self.hide_animated) 
        # 关闭按钮的对齐和样式可以保持不变，它会在所有设置项的下方
        main_settings_layout.addWidget(self.close_button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.hide() # 默认隐藏

        # 动画相关
        self.animation = QPropertyAnimation(self, b"geometry")
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity") # 改为 windowOpacity
        self.animation_group = QSequentialAnimationGroup(self) # 改为并行，或根据需要调整
                                                            # 使用 QParallelAnimationGroup 可能更适合同时缩放和淡化
        self.parallel_anim_group = QParallelAnimationGroup(self)
        self.parallel_anim_group.addAnimation(self.animation)
        self.parallel_anim_group.addAnimation(self.opacity_animation)

    def update_geometry_based_on_parent(self):
        """
        根据父窗口的大小重新计算并设置自己的几何形状。
        这应该在窗口已经显示且非动画状态时调用。
        """
        if not self.parentWidget() or not self.isVisible():
            # print("SettingsPage: Skipping geometry update - no parent or not visible.")
            return
        
        # 确保不在动画中 (这个检查在 NineSolverGUI.resizeEvent 中已经做了，这里可以作为双重保险)
        # if self.parallel_anim_group.state() != QParallelAnimationGroup.State.Idle:
        #     print("SettingsPage: Skipping geometry update - animating.")
        #     return
            
        parent_rect = self.parentWidget().rect()
        
        # --- 使用与 show_animated 中一致的计算逻辑 ---
        target_width = int(parent_rect.width() * 0.3) 
        min_sensible_width = 280 
        target_width = max(target_width, min_sensible_width)
        
        target_height = int(parent_rect.height() * 0.6)
        min_sensible_height = 200 # 你可以根据内容调整这个值
        target_height = max(target_height, min_sensible_height)
        # ---------------------------------------------

        target_x = parent_rect.center().x() - target_width // 2
        target_y = parent_rect.center().y() - target_height // 2
        
        new_geometry = QRect(target_x, target_y, target_width, target_height)

        if self.geometry() != new_geometry: 
            self.setGeometry(new_geometry)
            # print(f"SettingsPage geometry updated by parent resize to: {new_geometry}")

    def on_fumo_switch_changed(self, checked): # <--- 新增 Fumo 开关的槽函数
        """当Fumo开关状态改变时，发出信号。"""
        self.fumo_easter_egg_changed.emit(checked)

    # set_accumulate_switch_state 方法保持不变

    def set_fumo_switch_state(self, checked): # <--- 新增：从外部设置Fumo开关状态
        self.fumo_switch.setChecked(checked)
    # ---- 新增 Baka 声音的槽函数和 setter ----
    def on_baka_audio_switch_changed(self, checked):
        self.baka_audio_setting_changed.emit(checked)

    def set_baka_audio_switch_state(self, checked):
        self.baka_audio_switch.setChecked(checked)

    # ---- 新增：一个方法来从外部设置开关状态 (如果需要的话) ----
    def on_accumulate_switch_changed(self, checked):
        """当开关状态改变时，发出信号。"""
        self.accumulate_setting_changed.emit(checked)
    def set_accumulate_switch_state(self, checked):
        self.accumulate_switch.setChecked(checked)
    def show_animated(self):
        if not self.parentWidget():
            return

        parent_rect = self.parentWidget().rect()
        
        # ---- 新的目标尺寸：窄长条 ----
        # 宽度可以是一个固定值，或者父窗口的一个较小百分比
        # 例如，父窗口宽度的 40% 或 50%，或者一个固定像素值如 300px, 350px
        target_width = int(parent_rect.width() * 0.3) # 例如，父窗口宽度的 30%
        # 或者 target_width = 350 # 固定宽度示例
        
        # 高度可以保持原来的百分比，或者也调整一下
        target_height = int(parent_rect.height() * 0.6) # 高度可以不变
        # 确保宽度不会太小，至少能容纳内容
        min_sensible_width = 280 # 举个例子，最小合理宽度
        target_width = max(target_width, min_sensible_width)

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

# gui_main.py 或 widgets.py

# ... (必要的 QtWidget 和 QtCore 导入) ...

class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 阻止鼠标事件穿透到下面的控件
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False) 
        # 使背景透明（如果需要看到下面的内容，但我们主要用它来拦截事件）
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) 
        self.setStyleSheet("background-color: rgba(0,0,0,0);") # 完全透明
        # 或者用半透明调试:
        # self.setStyleSheet("background-color: rgba(255, 0, 0, 30);") 
        self.hide() 

    def setTargetWidget(self, widget_to_cover: QWidget):
        """设置此覆盖层要覆盖的目标控件，并同步大小和位置。"""
        if widget_to_cover and widget_to_cover.parentWidget():
            # 确保覆盖层和目标控件有相同的直接父控件，以保证坐标系一致
            if self.parent() != widget_to_cover.parentWidget():
                self.setParent(widget_to_cover.parentWidget())
            
            self.setGeometry(widget_to_cover.geometry())
            self.raise_() # 确保在目标控件之上
            print(f"Overlay set for widget: {widget_to_cover.objectName()} at {widget_to_cover.geometry()}")
        else:
            print("Warning: Invalid target widget or target widget has no parent for Overlay.")
            self.hide()

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

class FumoSplash(QWidget):
    def __init__(self, pixmap: QPixmap, 
                 parent_window_geometry_fallback: QRect, # 重命名以表明是备用
                 main_app_screen: Optional[QScreen] = None): # 新增参数 QScreen
        super().__init__()
        print(f"--- FumoSplash __init__ ---")
        if pixmap is None or pixmap.isNull():
            print("  FumoSplash __init__: Invalid pixmap, aborting.")
            return
 
        self.pixmap_original_size = pixmap.size() # 保存原始尺寸以供参考
        print(f"  FumoSplash __init__: Original pixmap size: {self.pixmap_original_size}")
        self.pixmap = pixmap
        self.main_app_screen = main_app_screen # 存储主程序屏幕
        self.parent_geo_fallback = parent_window_geometry_fallback # 保留备用

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SplashScreen 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.label = QLabel(self)
        # self.label.setPixmap(self.pixmap) # 推迟到 randomize 中设置缩放后的
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0) # 移除边距，让label填满
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setWindowOpacity(0.0) # <--- 直接设置窗口初始透明度
        print(f"  FumoSplash __init__: Initial opacity set to 0.0")

        self.animation_group = QSequentialAnimationGroup(self)
        
        self.fade_in_duration = 200  
        self.hold_duration = 100     
        self.fade_out_duration = 200 

        # 调用 _setup_and_start_animation
        # QTimer.singleShot(0, self._setup_and_start_animation) # 尝试用singleshot确保窗口系统已准备好
        self._setup_and_start_animation()


    def _setup_and_start_animation(self):
        print(f"--- FumoSplash _setup_and_start_animation ---")
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

        self.animation_group.finished.connect(self._on_animation_finished) # 改为连接到新方法

        print(f"  Calling _randomize_size_and_position...")
        self._randomize_size_and_position() 
        print(f"  Geometry after randomize: {self.geometry()}, Label pixmap size: {self.label.pixmap().size() if self.label.pixmap() else 'None'}")
        
        print(f"  Calling self.show()...")
        self.show()
        self.activateWindow() # 尝试激活
        self.raise_()         # 尝试提升到最前

        print(f"  self.show() called. Is visible: {self.isVisible()}, Window Opacity: {self.windowOpacity()}")
        
        print(f"  Starting animation group...")
        self.animation_group.start()
        print(f"  Animation group state after start: {self.animation_group.state()}")

    def _on_animation_finished(self):
        print(f"--- FumoSplash _on_animation_finished --- Closing window.")
        self.close()


    def _randomize_size_and_position(self):
        print(f"--- FumoSplash _randomize_size_and_position ---")
        if self.pixmap.isNull():
            print("  Pixmap is Null in randomize.")
            return

        all_screens = QApplication.instance().screens()
        if not all_screens:
            print("  No screens available, using main app window's screen or fallback geometry.")
            # 如果没有屏幕信息，就使用主程序窗口所在的屏幕（如果之前传入了）
            # 或者用 parent_geo_fallback 作为最后的备用
            if self.main_app_screen:
                target_screen_geometry = self.main_app_screen.geometry()
            else:
                target_screen_geometry = self.parent_geo_fallback
        else:
            # ---- 带权重的屏幕选择 ----
            primary_screen = QApplication.instance().primaryScreen() # 获取系统主屏幕
            main_app_screen_obj = self.main_app_screen # 主程序窗口当前所在的屏幕

            screens_to_choose_from = []
            weights = []

            # 确定主窗口当前屏幕的权重
            # 权重值可以调整
            main_screen_weight_target = 0.60 # 目标主屏幕出现概率
            if len(all_screens) == 1:
                main_screen_weight = 1.0 # 只有一个屏幕，100%
                other_screen_weight_each = 0.0
            elif len(all_screens) == 2:
                main_screen_weight = main_screen_weight_target # 例如 60%
                other_screen_weight_each = 1.0 - main_screen_weight # 剩余 40%
            elif len(all_screens) == 3:
                main_screen_weight = main_screen_weight_target # 例如 60%
                other_screen_weight_each = (1.0 - main_screen_weight) / 2 # 剩余平分，各 20%
            elif len(all_screens) == 4: # 你提到的例子
                main_screen_weight = 0.58
                other_screen_weight_each = (1.0 - main_screen_weight) / 3 # 约 14%
            else: # 更多屏幕，主屏幕至少55%，其余平分
                main_screen_weight = 0.55 
                if len(all_screens) > 1:
                    other_screen_weight_each = (1.0 - main_screen_weight) / (len(all_screens) - 1)
                else: # 实际上 len(all_screens) == 1 已经被上面处理了
                    other_screen_weight_each = 0 


            print(f"  Screen weights: Main App Screen target = {main_screen_weight*100:.1f}%, Other screens each target = {other_screen_weight_each*100:.1f}%")

            for screen in all_screens:
                screens_to_choose_from.append(screen)
                if main_app_screen_obj and screen == main_app_screen_obj:
                    weights.append(main_screen_weight)
                    print(f"    Screen '{screen.name()}' is MAIN APP SCREEN, weight: {main_screen_weight}")
                elif screen == primary_screen and not main_app_screen_obj: # 如果无法确定主程序屏幕，则用系统主屏
                     weights.append(main_screen_weight)
                     print(f"    Screen '{screen.name()}' is PRIMARY (fallback), weight: {main_screen_weight}")
                else:
                    weights.append(other_screen_weight_each)
                    print(f"    Screen '{screen.name()}' is OTHER, weight: {other_screen_weight_each}")
            
            # 如果权重列表为空或所有权重为0（不太可能，除非只有一个屏幕且权重计算错误），则均等选择
            if not weights or all(w == 0 for w in weights):
                print("  Warning: Weights are zero or empty, falling back to uniform random choice.")
                chosen_screen = random.choice(all_screens)
            else:
                # 使用 random.choices 进行带权随机选择
                # random.choices 返回一个列表，我们取第一个元素
                chosen_screen_list = random.choices(screens_to_choose_from, weights=weights, k=1)
                chosen_screen = chosen_screen_list[0]
            
            target_screen_geometry = chosen_screen.geometry()
            print(f"  Chosen screen (weighted): '{chosen_screen.name()}', Geometry: {target_screen_geometry}")
            # -----------------------------

        # ---- 随机大小计算 (与之前类似，但基于新的 target_screen_geometry) ----
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

        print(f"  Calculated Fumo scaled size: {scaled_width}x{scaled_height} (Target dim: {target_fumo_dimension})")

        self.label.setPixmap(self.pixmap.scaled(scaled_width, scaled_height, 
                                                Qt.AspectRatioMode.KeepAspectRatio, 
                                                Qt.TransformationMode.SmoothTransformation))
        self.resize(scaled_width, scaled_height) 
        # -----------------------------------

        # ---- 随机位置计算 (与之前类似，基于新的 target_screen_geometry) ----
        max_x_offset_on_screen = target_screen_geometry.width() - scaled_width
        max_y_offset_on_screen = target_screen_geometry.height() - scaled_height
        
        print(f"  Screen for positioning: X={target_screen_geometry.x()}, Y={target_screen_geometry.y()}, W={target_screen_geometry.width()}, H={target_screen_geometry.height()}")
        print(f"  Max X offset on screen: {max_x_offset_on_screen}, Max Y offset on screen: {max_y_offset_on_screen}")

        rand_x_on_screen_offset = 0
        rand_y_on_screen_offset = 0

        if max_x_offset_on_screen > 0:
            rand_x_on_screen_offset = random.randint(0, max_x_offset_on_screen)
        
        if max_y_offset_on_screen > 0:
            rand_y_on_screen_offset = random.randint(0, max_y_offset_on_screen)
            
        final_screen_x = target_screen_geometry.x() + rand_x_on_screen_offset
        final_screen_y = target_screen_geometry.y() + rand_y_on_screen_offset
            
        print(f"  Calculated final screen position: X={final_screen_x}, Y={final_screen_y}")
        self.move(final_screen_x, final_screen_y)
        # -----------------------------------------

    def paintEvent(self, event: QPaintEvent): 
        # print("FumoSplash Paint Event") # 可以取消注释以查看是否被频繁调用
        # super().paintEvent(event) # 对于完全透明的widget，可能不需要调用父类
        # 如果背景完全透明，QLabel会自己绘制
        super().paintEvent(event) # 我们依赖 WA_TranslucentBackground 和 QLabel 来绘制

class MainContentWidget(QWidget):
    """一个自定义的QWidget，它在每次paintEvent时发出一个信号。"""
    paintEventTriggered = pyqtSignal()

    def paintEvent(self, event: QPaintEvent):
        # 首先调用父类的paintEvent来完成标准绘制
        super().paintEvent(event)
        # 然后发出信号，通知父窗口（NineSolverGUI）现在是更新位置的最佳时机
        self.paintEventTriggered.emit()

class NineSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__() 
        self.calculate_button_overlay = None # 初始化计算按钮上方透明窗口
        self.clear_button_overlay = None # <--- 新增：为清除按钮声明覆盖层      
        self.current_theme = get_system_theme() # 获取初始系统主题
        self._theme_initialized = False # 添加一个标志位        
        self.accumulate_results = False # 新增：用于控制是否累积结果
        self.show_fumo_easter_egg = False # <--- 新增：Fumo彩蛋开关状态，默认关闭
        self.play_baka_audio_on_success = True # <--- 新增：Baka声音开关状态，默认开启
        self.fumo_pixmap = None # <--- 新增：用于存储加载后的Fumo QPixmap
        self.calculate_button_overlay = None
        # 新增：预加载 Fumo 图片
        try:
            fumo_image = QImage.fromData(base64.b64decode(FUMO))
            if not fumo_image.isNull():
                self.fumo_pixmap = QPixmap.fromImage(fumo_image)
                print("Fumo pixmap loaded successfully.")
            else:
                print("Failed to load Fumo image from base64 data.")
        except Exception as e:
            print(f"Error loading Fumo pixmap: {e}")

        self.ICON_DATA = ICON_DATA
        # 存储所有成功计算的结果
        self.historical_results = []
        
        # 新增：预加载设置图标
        self.setting_icon_light = QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(SETTING_GREY))))
        self.setting_icon_dark = QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(SETTING_GREEN))))

        # 初始化模糊效果
        self.blur_effect = QGraphicsBlurEffect(self) # 父对象可以是 self
        self.blur_effect.setBlurRadius(0)  # 设置模糊半径，可以调整
        self.blur_effect.setEnabled(False) # 默认不启用

        # --- 添加代码 ---
        self.settings_button_opacity_effect = QGraphicsOpacityEffect(self)
        self.settings_button_opacity_effect.setOpacity(1.0) # 初始完全不透明
        

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
        # 实例化设置页面
        self.settings_page = SettingsPage(
            self, 
            initial_accumulate_state=self.accumulate_results,
            initial_fumo_state=self.show_fumo_easter_egg, # <--- 传递 Fumo 初始状态
            initial_baka_audio_state=self.play_baka_audio_on_success,# <--- 传递 Baka 声音初始状态
            fumo_icon_pixmap=self.fumo_pixmap             # <--- 传递 Fumo Pixmap 作为图标
        )
        self.settings_page.closed.connect(self.on_settings_page_fully_closed)
        self.settings_page.hide_animation_started.connect(self.on_settings_hide_anim_started) 
        self.settings_page.accumulate_setting_changed.connect(self.on_accumulate_setting_changed)
        self.settings_page.fumo_easter_egg_changed.connect(self.on_fumo_easter_egg_changed)
        self.settings_page.baka_audio_setting_changed.connect(self.on_baka_audio_setting_changed) # <--- 连接baka信号



        self.setWindowTitle("⑨")
        self.setMinimumSize(800, 600)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(self.ICON_DATA)))))
        self.init_ui()
        if hasattr(self, 'calculate_btn'):
            self.calculate_button_overlay = OverlayWidget(self.calculate_btn.parentWidget())
        self.setup_animations()

        # 连接系统调色板变化信号
        QApplication.instance().paletteChanged.connect(self.handle_theme_change)

    def _sync_clone_position_on_paint(self):
        """
        在paintEvent触发时调用，以最快速度同步克隆按钮的位置。
        """
        if hasattr(self, 'cloned_settings_button') and self.cloned_settings_button.isVisible():
            
            #--- 修改代码 ---
            # 使用 mapTo 将原始按钮的左上角(0,0)位置映射到 main_central_widget 的坐标系中。
            # 这是获取 "孙子" 控件在 "祖父" 控件中位置的正确方法。
            target_pos = self.settings_button.mapTo(self.main_central_widget, QPoint(0, 0))

            # 移动克隆按钮到计算出的精确位置
            if self.cloned_settings_button.pos() != target_pos:
                self.cloned_settings_button.move(target_pos)

            # 为保险起见，同时同步大小。
            if self.cloned_settings_button.size() != self.settings_button.size():
                 self.cloned_settings_button.setFixedSize(self.settings_button.size())

    def resizeEvent(self, event: QResizeEvent): 
        super().resizeEvent(event)
        # print(f"--- NineSolverGUI resizeEvent --- New size: {event.size()}")

        # 2. 更新设置页面的位置和大小 (这个逻辑保持不变)
        if hasattr(self, 'settings_page') and self.settings_page.isVisible():
            if self.settings_page.parallel_anim_group.state() == QAbstractAnimation.State.Stopped and \
               abs(self.settings_page.windowOpacity() - 1.0) < 0.01:
                if hasattr(self.settings_page, 'update_geometry_based_on_parent'):
                    self.settings_page.update_geometry_based_on_parent()

    def _synchronize_cloned_button(self):
        """
        在需要完全同步克隆按钮时调用（例如，在它将要显示之前，或窗口首次显示时）。
        同步大小、图标大小、图标内容（通过调用样式更新）和位置。
        """
        if not hasattr(self, 'settings_button') or not hasattr(self, 'cloned_settings_button'):
            return
        # print("SYNC_FULL: _synchronize_cloned_button called")
        
        # 1. 同步大小和IconSize
        original_size = self.settings_button.size()
        original_icon_size = self.settings_button.iconSize()

        if self.cloned_settings_button.size() != original_size:
            self.cloned_settings_button.setFixedSize(original_size)
        if self.cloned_settings_button.iconSize() != original_icon_size:
            self.cloned_settings_button.setIconSize(original_icon_size)
        
        # 2. 更新图标内容 (通过调用样式更新，确保主题正确)
        self._update_cloned_button_style() 
                
        # 4. 确保层级 (如果克隆按钮当前应该可见，虽然调用此函数时它可能正要显示)
        if self.cloned_settings_button.isVisible(): 
            self.cloned_settings_button.raise_()    
    
    def on_baka_audio_setting_changed(self, checked):
        """处理来自设置页面的Baka音效设置变化。"""
        self.play_baka_audio_on_success = checked
        print(f"Play Baka audio setting changed to: {self.play_baka_audio_on_success}")
    def on_fumo_easter_egg_changed(self, checked):
        """处理来自设置页面的Fumo彩蛋设置变化。"""
        self.show_fumo_easter_egg = checked
        print(f"Fumo easter egg setting changed to: {self.show_fumo_easter_egg}")
    def trigger_fumo_splash(self):
        # ... (前面的打印和条件检查不变) ...
        print(f"--- trigger_fumo_splash called ---") 
        print(f"  show_fumo_easter_egg: {self.show_fumo_easter_egg}")
        fumo_pixmap_is_valid = False
        if hasattr(self, 'fumo_pixmap') and self.fumo_pixmap and not self.fumo_pixmap.isNull():
            fumo_pixmap_is_valid = True
            print(f"  fumo_pixmap is valid: True, Size: {self.fumo_pixmap.size()}")
        else:
            print(f"  fumo_pixmap is valid: False or not loaded.")

        if not self.show_fumo_easter_egg:
            print("  Fumo splash not shown: show_fumo_easter_egg is False.")
            return
        if not fumo_pixmap_is_valid: 
            print("  Fumo splash not shown: fumo_pixmap is invalid or not loaded.")
            return

        main_window_geometry = self.geometry() # 这个是相对于虚拟桌面的
        print(f"  Main window geometry for Fumo: {main_window_geometry}")
        
        if not self.isVisible():
            print("  Main window is not visible, Fumo splash might not display correctly.")
            # return 

        # ---- 新增：获取主窗口当前所在的屏幕 ----
        current_screen_of_main_window = self.screen() # QWidget.screen() 获取 widget 所在的屏幕
        if current_screen_of_main_window is None: # Fallback if screen somehow cannot be determined
            screens = QApplication.instance().screens()
            if screens:
                current_screen_of_main_window = QApplication.instance().primaryScreen() or screens[0]
            else: # Should not happen
                print("  Could not determine current screen, Fumo may not display.")
                return 
        print(f"  Main window is on screen: {current_screen_of_main_window.name() if current_screen_of_main_window else 'Unknown'}")    

        print(f"  Attempting to create FumoSplash instance...")
        try:
            # ---- 修改：传递当前屏幕给 FumoSplash ----
            splash_instance = FumoSplash(
                self.fumo_pixmap, 
                main_window_geometry, # 这个参数现在可以移除，或作为备用
                current_screen_of_main_window # 新增参数
            )     
            print(f"  FumoSplash instance created: {splash_instance}")
        except Exception as e:
            print(f"  Error creating FumoSplash instance: {e}")
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
        
    def toggle_settings_page(self):
        settings_page_anim_running = self.settings_page.parallel_anim_group.state() == QParallelAnimationGroup.State.Running
        blur_anim_running = self.blur_animation.state() == QPropertyAnimation.State.Running

        if settings_page_anim_running or blur_anim_running:
            print("Animation in progress, ignoring toggle request.")
            return

        target_blur_radius = 10
        animation_duration = 300 

        if self.settings_page.isVisible(): # === 关闭设置页面 ===
            print("Toggle: Settings page is visible, hiding it.")
            self.settings_page.hide_animated() 
            
            # ---- 恢复主界面交互 ----
            if hasattr(self, 'input_field'):
                self.input_field.setEnabled(True)
                # self.input_field.setFocus() # 焦点在 on_settings_page_fully_closed 中设置更合适

            if self.calculate_button_overlay:
                self.calculate_button_overlay.hide()
            
            if self.clear_button_overlay:
                self.clear_button_overlay.hide()
            
            if hasattr(self, 'input_field'):
                try: # 尝试断开 dummy，以防万一
                    self.input_field.returnPressed.disconnect(self.on_enter_pressed_disabled_dummy)
                except TypeError: pass
                try: # 先断开，再连接，防止重复连接
                    self.input_field.returnPressed.disconnect(self.on_enter_pressed)
                except TypeError: pass
                self.input_field.returnPressed.connect(self.on_enter_pressed)
            # -------------------------

        else: # === 打开设置页面 ===
            print("Toggle: Settings page is hidden, showing it.")
            
            if hasattr(self.settings_page, 'set_accumulate_switch_state'):
                self.settings_page.set_accumulate_switch_state(self.accumulate_results)
            if hasattr(self.settings_page, 'set_fumo_switch_state'):
                self.settings_page.set_fumo_switch_state(self.show_fumo_easter_egg)
            if hasattr(self.settings_page, 'set_baka_audio_switch_state'):
                self.settings_page.set_baka_audio_switch_state(self.play_baka_audio_on_success)
            
     
            self._update_cloned_button_style() # 确保图标正确
            self._synchronize_cloned_button()
            self.settings_button_opacity_effect.setOpacity(0.0)
            self.cloned_settings_button.show()
            self.cloned_settings_button.raise_()           

            # ---- 禁用主界面交互 ----
            if hasattr(self, 'input_field'):
                self.input_field.setEnabled(False)

            if self.calculate_button_overlay and hasattr(self, 'calculate_btn'):
                # 确保在设置覆盖层几何前，布局是最新的
                QApplication.processEvents() 
                if self.calculate_btn.isVisible() and self.calculate_btn.geometry().isValid():
                    self.calculate_button_overlay.setTargetWidget(self.calculate_btn)
                    self.calculate_button_overlay.show()
                    print(f"Overlay shown over calculate_btn at {self.calculate_btn.geometry()}")
                else:
                    print("Warning: Calculate button not ready or not visible for overlay.")
                    self.calculate_button_overlay.hide()
                # ---------- 新增：处理清除按钮覆盖层 ----------
            if self.clear_button_overlay and hasattr(self, 'clear_button'):
                QApplication.processEvents() # 确保布局更新
                if self.clear_button.isVisible() and self.clear_button.geometry().isValid():
                    self.clear_button_overlay.setTargetWidget(self.clear_button)
                    self.clear_button_overlay.show()
                    print(f"Overlay shown over clear_button at {self.clear_button.geometry()}")
                else:
                    print("Warning: Clear button not ready or not visible for overlay.")
                    self.clear_button_overlay.hide()

            if hasattr(self, 'input_field'):
                try:
                    self.input_field.returnPressed.disconnect(self.on_enter_pressed)
                    # 可选连接到dummy，主要目的是确保旧的连接已断开
                    # self.input_field.returnPressed.connect(self.on_enter_pressed_disabled_dummy)
                except TypeError:
                    print("Could not disconnect on_enter_pressed (maybe not connected).")
            # -------------------------

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
    def on_enter_pressed_disabled_dummy(self):
        """一个空槽函数，用于在禁用回车计算时临时连接，或仅作为标记。"""
        # print("Enter pressed while settings are open (dummy handler).")
        pass
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
        
        if hasattr(self, 'cloned_settings_button') and self.cloned_settings_button.isVisible():
            print("Hiding cloned_settings_button, showing original settings_button.")
            self.cloned_settings_button.hide()
            if hasattr(self, 'cloned_button_opacity_effect'): # 检查是否存在
                 if self.cloned_button_opacity_effect: # 再次检查是否为None
                    self.cloned_button_opacity_effect.setOpacity(1.0) 

        if hasattr(self, 'settings_button_opacity_effect'):
            self.settings_button_opacity_effect.setOpacity(1.0)
        
        if hasattr(self, '_update_settings_button_style'):
            self._update_settings_button_style() 
        
        # ---- 新增：恢复主界面交互 ----
        if hasattr(self, 'input_field'):
            self.input_field.setEnabled(True)
            self.input_field.setFocus() # 将焦点还给输入框
        
        if hasattr(self, 'calculate_button_overlay') and self.calculate_button_overlay: # 确保已创建
            self.calculate_button_overlay.hide()

        if hasattr(self, 'clear_button_overlay') and self.clear_button_overlay:
            self.clear_button_overlay.hide()
        
        if hasattr(self, 'input_field'):
            try: # 尝试断开 dummy
                self.input_field.returnPressed.disconnect(self.on_enter_pressed_disabled_dummy)
            except TypeError: pass
            try: # 先断开，再连接，防止重复连接
                self.input_field.returnPressed.disconnect(self.on_enter_pressed)
            except TypeError: pass
            self.input_field.returnPressed.connect(self.on_enter_pressed)
         
    # 在 NineSolverGUI 类中

    def showEvent(self, event_obj: QEvent):
        super().showEvent(event_obj) 
        if not self._theme_initialized: 
            self.apply_theme_styling(self.current_theme, force_active_on_initial_show=True) 
        
        # 确保在窗口显示后，克隆按钮的位置和样式是正确的
        # 使用 QTimer.singleShot 确保布局已经稳定
        if hasattr(self, '_synchronize_cloned_button'): 
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
        self.main_central_widget = MainContentWidget()
        self.main_central_widget.paintEventTriggered.connect(self._sync_clone_position_on_paint) # <-- 连接信号 
        self.setCentralWidget(self.main_central_widget) 
        main_layout = QVBoxLayout(self.main_central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15) # 统一间距

        # ---- 新增：创建克隆齿轮按钮 ----
        self.cloned_settings_button = QPushButton(self) # 父对象是主窗口 self
        self.cloned_settings_button.setObjectName("clonedSettingsButton")
        # 外观属性将在 init_ui 后，根据原始按钮设置，并由 _update_cloned_button_style 更新
        self.cloned_settings_button.setFlat(True)
        self.cloned_settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cloned_settings_button.hide() # 默认隐藏
        self.cloned_settings_button.clicked.connect(self.toggle_settings_page) # 点击也触发toggle

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
        self.settings_button.setGraphicsEffect(self.settings_button_opacity_effect)

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

        # self.main_frame 是 input_layout (包含 calculate_btn) 的容器的 widget
        if hasattr(self, 'main_frame'): 
            self.calculate_button_overlay = OverlayWidget(self.main_frame)
        else: # Fallback, though main_frame should exist
            self.calculate_button_overlay = OverlayWidget(self.main_central_widget)
        
        # 分隔线
        self.separator = QFrame()
        self.separator.setObjectName("separator")
        self.separator.setFrameShape(QFrame.Shape.HLine)
        frame_layout.addWidget(self.separator)
        
         # ---- 结果区域标题和清除按钮的布局 ----
        results_header_layout = QHBoxLayout() # 新建一个水平布局
        results_header_layout.setSpacing(10) # 设置间距

        self.result_title = QLabel("计算结果")
        self.result_title.setObjectName("result_title")
        # 让标题标签在水平方向上尽可能扩展，将按钮推向右侧
        self.result_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred) 
        results_header_layout.addWidget(self.result_title)

        # results_header_layout.addStretch(1) # 或者在这里添加一个伸展项将按钮推到最右边

        self.clear_button = AnimatedPushButton("清除") # <--- 创建清除按钮
        self.clear_button.setObjectName("clearResultsButton") # 给它一个对象名以便样式控制（如果需要）
        # 设置固定大小策略，与“计算”按钮一致
        self.clear_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed) 
        # 你可能需要根据 "计算" 按钮的实际宽度调整这里的 min/max-width，或者让 AnimatedPushButton 自己处理
        # 如果 AnimatedPushButton 的样式已经包含了 min/max width，这里可能不需要再设
        # self.clear_button.setMinimumWidth(60) # 与计算按钮的样式一致
        # self.clear_button.setMaximumWidth(80) # 与计算按钮的样式一致
        self.clear_button.clicked.connect(self.clear_results_display) # <--- 连接到新的槽函数
        results_header_layout.addWidget(self.clear_button)

        frame_layout.addLayout(results_header_layout) # 将这个水平布局添加到垂直的 frame_layout

        # ---- 新增：在 clear_button 之后创建其覆盖层 ----
        # 父对象应该是 self.clear_button 所在的容器，这里也是 self.main_frame
        if hasattr(self, 'main_frame'):
            self.clear_button_overlay = OverlayWidget(self.main_frame)
        else: # Fallback
            self.clear_button_overlay = OverlayWidget(self.main_central_widget)
        
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

    def clear_results_display(self):
        """
        清除 QTextEdit 中的所有内容、历史记录，并重置相关状态。
        """
        print("Clearing results display.")
        self.result_display.clear()
        self.historical_results = []
        
        # 如果你将来重新引入了类似 results_count_for_separator 的计数器，也在这里重置
        # self.results_count_for_separator = 0 

        # 可选：更新状态栏
        self.status_label.setText("输出已清除")

        # 可选：将焦点移回输入框
        if hasattr(self, 'input_field'):
            self.input_field.setFocus()    
    def show_result(self, target_str: str, expr_str: str, elapsed: float): # Renamed expr to expr_str
        self.stop_loading_animation()
        
        new_result_entry = {
            'target': target_str,
            'expr': expr_str,
            'elapsed': elapsed,
            'type': 'success' if expr_str else 'not_found'
        }
        
        # 检查是否有噪声剔除信息需要显示
        if hasattr(self, '_current_noise_info'):
            new_result_entry['noise_info'] = self._current_noise_info
            delattr(self, '_current_noise_info')  # 清除临时信息

        if self.accumulate_results:
            self.historical_results.append(new_result_entry)
            self._render_all_historical_results() # 渲染所有累积的结果
        else:
            # 非累积模式，只显示当前这一个 (可以临时存到historical_results[0]或单独变量)
            self.historical_results = [new_result_entry] # 或者用独立的 _last_... 变量
            self._render_all_historical_results() # 也可以调用它，它会清空并只渲染这一个

        if expr_str: 
            self.status_label.setText(f"计算完成 - 耗时 {elapsed:.2f}秒")
            if self.play_baka_audio_on_success: # <--- 检查开关状态
                finder = ImprovedNineExpressionFinder() 
                finder.play_baka_sound()
            self.trigger_fumo_splash()
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
    
    def _filter_and_parse_input(self, raw_input: str) -> tuple:
        """从混合字符中提取数字和运算符，计算结果并返回原始表达式和计算结果"""
        import re
        
        # 保留数字、运算符和小数点
        filtered = re.sub(r'[^0-9+\-*/.]', '', raw_input)
        
        if not filtered:
            raise ValueError("输入中没有有效的数字或运算符")
        
        # 处理连续的运算符，保留最后一个
        filtered = re.sub(r'[+\-*/]{2,}', lambda m: m.group()[-1], filtered)
        
        # 移除开头和结尾的运算符（除了负号）
        if filtered and filtered[0] in '+*/':
            filtered = filtered[1:]
        if filtered and filtered[-1] in '+-*/':
            filtered = filtered[:-1]
            
        if not filtered:
            raise ValueError("过滤后没有有效内容")
        
        try:
            # 安全计算表达式
            result = eval(filtered)
            return filtered, result
        except:
            # 如果表达式无效，尝试提取第一个数字
            numbers = re.findall(r'\d+(?:\.\d+)?', filtered)
            if numbers:
                return numbers[0], float(numbers[0])
            else:
                raise ValueError("无法解析有效的数学表达式")
    
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

            # 新增：噪声剔除和表达式解析
            if any(c.isalpha() for c in input_text) or any(c in '!@#$%^&()[]{}|\\:;"<>?,~`' for c in input_text):
                # 包含字母或特殊字符，需要过滤
                filtered_expr, calculated_result = self._filter_and_parse_input(input_text)
                
                # 保存噪声剔除信息供show_result使用
                self._current_noise_info = {
                    'original_input': input_text,
                    'filtered_expr': filtered_expr,
                    'calculated_result': calculated_result
                }
                
                # 显示过滤和计算过程
                process_info = f"原始输入: {input_text}\n提取表达式: {filtered_expr}\n计算结果: {calculated_result}"
                print(process_info)
                
                # 使用计算结果作为目标值
                target_value = int(calculated_result)
            elif 'e' in input_text.lower():
                # Set precision for Decimal. Default is 28, which is usually enough.
                # For very large numbers like 1e100, you might need more.
                # Let's set it to a sufficiently large value.
                getcontext().prec = len(input_text.split('e')[0]) + int(input_text.split('e')[1]) + 5
                target_value = int(Decimal(input_text))
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
        error_html_color = '#ff6b6b' if self.current_theme == 'dark' else '#d9534f'
        # --- 颜色逻辑结束 ---

        for index, entry in enumerate(self.historical_results):
            entry_inner_html = ""

            if entry['type'] == 'success' or entry['type'] == 'not_found':
                target_str = entry['target']
                expr_str = entry.get('expr') 
                elapsed = entry.get('elapsed', 0.0)

                if expr_str: # 成功找到表达式
                    # 检查是否有噪声剔除信息
                    noise_info_html = ""
                    if 'noise_info' in entry:
                        noise_info = entry['noise_info']
                        noise_info_html = f"""
                        <p style="color: {time_color}; font-style: italic;">噪声剔除过程:</p>
                        <p style="color: {time_color}; font-size: 12px;">原始输入: {noise_info['original_input']}</p>
                        <p style="color: {time_color}; font-size: 12px;">提取表达式: {noise_info['filtered_expr']}</p>
                        <p style="color: {time_color}; font-size: 12px;">计算结果: {noise_info['calculated_result']}</p>
                        """
                    
                    entry_inner_html = f"""
                        <p>目标: <span style="font-weight: bold;">{target_str}</span></p>
                        {noise_info_html}
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
        # 直接关闭程序
        event.accept()
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序字体
    font = QFont()
    font.setFamily("Microsoft YaHei" if sys.platform == "win32" else "PingFang SC")
    app.setFont(font)
    
    window = NineSolverGUI()
    window.show()
    sys.exit(app.exec())