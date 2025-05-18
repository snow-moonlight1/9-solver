# gui_main.py
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QSizePolicy, 
                             QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QPalette
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

# 浅色主题样式表 (大部分是你已有的)
LIGHT_STYLESHEET = """
    QMainWindow {
        background-color: #f3f3f3; /* 浅色背景 */
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
    NineSolverGUI #example_label {
        color: #adb5bd; font-size: 12px;
    }
    NineSolverGUI #separator {
        color: #e9ecef;
    }
    NineSolverGUI #result_title {
        font-size: 16px; font-weight: bold; color: #343a40;
    }
"""

# 深色主题样式表
DARK_STYLESHEET = """
    QMainWindow {
        background-color: #202020; /* 深色背景 */
    }
    QLabel {
        color: #e0e0e0; /* 浅色文字 */
    }
    QPushButton {
        background-color: #5a98e4; /* 按钮颜色可微调以适应深色背景 */
        color: white; /* 文字保持白色 */
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 14px;
        min-width: 60px;
        max-width: 80px;
    }
    QPushButton:hover {
        background-color: #4a88d4;
    }
    QPushButton:disabled {
        background-color: #555555;
        color: #999999;
    }
    QLineEdit {
        padding: 8px;
        border: 1px solid #555555; /* 深色边框 */
        border-radius: 4px;
        font-size: 16px;
        background-color: #333333; /* 深色输入框背景 */
        color: #e0e0e0; /* 浅色文字 */
    }
    QLineEdit:focus {
        border: 1px solid #5a98e4; /* 高亮边框 */
        background-color: #404040;
    }
    QTextEdit {
        padding: 12px;
        border: 1px solid #555555; /* 深色边框 */
        border-radius: 4px;
        font-family: Consolas, 'Courier New', monospace;
        font-size: 14px;
        background-color: #333333; /* 深色文本编辑区背景 */
        color: #e0e0e0; /* 浅色默认文字 */
    }
    #main_frame {
        background-color: #2c2c2c; /* 稍浅于主背景的深色 */
        border-radius: 8px;
        border: 1px solid #444444; /* 深色边框 */
    }
    #status_label { /* 确保状态栏标签有特定样式 */
        color: #aaaaaa; /* 浅灰色文字 */
        font-style: italic;
    }
    /* 深色模式下的特殊颜色调整 */
    NineSolverGUI #title_label { /* 更精确地指定标题标签 */
        color: #5a98e4; margin-bottom: 10px; /* 保持或调整品牌色 */
    }
    NineSolverGUI #description { /* 更精确地指定描述标签 */
        color: #aaaaaa; font-size: 14px;
    }
    NineSolverGUI #example_label {
        color: #888888; font-size: 12px;
    }
    NineSolverGUI #separator {
        color: #444444; /* 深色分隔线 */
    }
    NineSolverGUI #result_title {
        font-size: 16px; font-weight: bold; color: #d0d0d0; /* 浅色标题 */
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
        self.current_theme = "light" # 默认主题，会被检测结果覆盖
        
        # 初始化系统托盘
        self.tray_icon = QSystemTrayIcon(self)
        self.ICON_DATA = ICON_DATA  
        from PyQt6.QtGui import QImage
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
        # 检测并应用主题
        detected_theme = get_system_theme()
        self.apply_theme_styling(detected_theme)
        
    def apply_theme_styling(self, theme_name):
        """应用指定的主题样式表"""
        if theme_name == "dark":
            self.setStyleSheet(DARK_STYLESHEET)
            self.current_theme = "dark"
        else: # 默认为浅色
            self.setStyleSheet(LIGHT_STYLESHEET)
            self.current_theme = "light"
        
        # 如果状态栏标签动画颜色依赖主题，可以在这里重新配置或在动画函数中判断
        # 例如，确保动画停止后颜色正确
        self.stop_loading_animation() # 会根据 self.current_theme 设置正确颜色
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
        self.input_field.setPlaceholderText("请输入目标整数...")
        self.input_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        input_layout.addWidget(self.input_field)
        
        self.calculate_btn = AnimatedPushButton("计算")
        self.calculate_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.calculate_btn.clicked.connect(self.start_calculation)
        input_layout.addWidget(self.calculate_btn)
        
        frame_layout.addLayout(input_layout)
        
        # 示例提示
        self.example_label = QLabel("示例: 123, -456, 1e3")
        self.example_label.setObjectName("example_label")
        frame_layout.addWidget(self.example_label)
        
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

        # 在 NineSolverGUI 类中:
    def show_result(self, target, expr, elapsed):
        self.stop_loading_animation()
        
        # 根据当前主题确定文本和特定颜色
        default_text_color = "#e0e0e0" if self.current_theme == "dark" else "#212529"
        time_color = "#aaaaaa" if self.current_theme == "dark" else "#6c757d"
        expr_color = "#5fa8ff" if self.current_theme == "dark" else "#4a90e2" # 蓝色系，深色下可以亮一点
        baka_color = "#2c9fff" if self.current_theme == "dark" else "#0165cc" # Baka颜色也可以调整

        if expr:
            self.result_display.setHtml(f"""
                <div style="font-family: Consolas, 'Courier New', monospace; font-size: 14px; color: {default_text_color};">
                    <p>目标: <span style="font-weight: bold;">{target}</span></p>
                    <p>结果 (<span style="color: {time_color};">{elapsed:.2f}秒</span>):</p>
                    <p><span style="font-weight: bold;">{target}</span> = <span style="color: {expr_color};">{expr}</span></p>
                    <p style="color: {baka_color}; font-weight: bold;">baka~</p>
                </div>
            """)
            
            self.status_label.setText(f"计算完成 - 耗时 {elapsed:.2f}秒")
            
            finder = ImprovedNineExpressionFinder()
            finder.play_baka_sound()
        else:
            # 对于纯文本，QTextEdit 的 stylesheet 已经处理了颜色
            self.result_display.setPlainText(f"无法找到 {target} 的有效表达式")
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
        
    def start_calculation(self):
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