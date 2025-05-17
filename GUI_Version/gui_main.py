# gui_main.py
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from main import ImprovedNineExpressionFinder
import time

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
        self.setWindowTitle("⑨")
        self.setMinimumSize(800, 600)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon("assets/icon.ico"))
        
        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f3f3;
            }
            QLabel {
                color: #495057;
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
            }
            #main_frame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            #status_label {
                color: #6c757d;
                font-style: italic;
            }
        """)
        
        self.init_ui()
        self.setup_animations()
        
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
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #4a90e2; margin-bottom: 10px;")
        title_layout.addWidget(self.title_label)
        
        self.description = QLabel("输入一个整数，琪露诺会尝试用9、99、999的加减乘除组合来表示它")
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description.setStyleSheet("color: #6c757d; font-size: 14px;")
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
        self.example_label.setStyleSheet("color: #adb5bd; font-size: 12px;")
        frame_layout.addWidget(self.example_label)
        
        # 分隔线
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setStyleSheet("color: #e9ecef;")
        frame_layout.addWidget(self.separator)
        
        # 结果区域
        self.result_title = QLabel("计算结果")
        self.result_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #343a40;")
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
        color1 = QColor("#6c757d")
        color2 = QColor("#adb5bd")
        
        self.loading_animation.stop()
        self.loading_animation.setStartValue(color1)
        self.loading_animation.setEndValue(color2)
        self.loading_animation.start()
    
    def stop_loading_animation(self):
        """停止加载动画"""
        self.loading_animation.stop()
        self.status_label.setStyleSheet("color: #6c757d;")
    
    def cleanup_after_calculation(self):
        """计算完成后清理输入框并恢复按钮状态"""
        self.input_field.clear()
        self.calculate_btn.setEnabled(True)
        self.input_field.setFocus()
        
        # 停止加载动画
        self.stop_loading_animation()
    
    def show_result(self, target, expr, elapsed):
        self.stop_loading_animation()
        
        if expr:
            # 设置彩色文本
            self.result_display.setHtml(f"""
                <div style="font-family: Consolas, 'Courier New', monospace; font-size: 14px;">
                    <p>目标: <span style="font-weight: bold;">{target}</span></p>
                    <p>结果 (<span style="color: #6c757d;">{elapsed:.2f}秒</span>):</p>
                    <p><span style="font-weight: bold;">{target}</span> = <span style="color: #4a90e2;">{expr}</span></p>
                    <p style="color: #0165cc; font-weight: bold;">baka~</p>
                </div>
            """)
            
            self.status_label.setText(f"计算完成 - 耗时 {elapsed:.2f}秒")
            
            # 播放声音
            finder = ImprovedNineExpressionFinder()
            finder.play_baka_sound()
        else:
            self.result_display.setPlainText(f"无法找到 {target} 的有效表达式")
            self.status_label.setText("未找到结果")
    
    def show_error(self, error_msg):
        self.result_display.setPlainText(f"错误: {error_msg}")
        self.status_label.setText("发生错误")
        self.stop_loading_animation()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序字体
    font = QFont()
    font.setFamily("Microsoft YaHei" if sys.platform == "win32" else "PingFang SC")
    app.setFont(font)
    
    window = NineSolverGUI()
    window.show()
    sys.exit(app.exec())