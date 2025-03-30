# gui_main.py
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
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

class NineSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⑨ 表达式求解器")
        self.setMinimumSize(800, 600)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon("assets/icon.ico"))
        
        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #495057;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 80px;
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
        """)
        
        self.init_ui()
        
    def init_ui(self):
        # 主部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题区域 (无边框)
        title_layout = QVBoxLayout()
        title_layout.setSpacing(10)
        
        title_label = QLabel("⑨ 表达式求解器")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #4a90e2; margin-bottom: 10px;")
        title_layout.addWidget(title_label)
        
        description = QLabel("输入一个整数，琪露诺会尝试用9、99、999的加减乘除组合来表示它")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #6c757d; font-size: 14px;")
        title_layout.addWidget(description)
        
        main_layout.addLayout(title_layout)
        
        # 主内容区域 (单个边框)
        main_frame = QWidget()
        main_frame.setObjectName("main_frame")
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(20)
        
        # 输入区域 (无边框)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("请输入目标整数...")
        input_layout.addWidget(self.input_field)
        
        self.calculate_btn = QPushButton("计算")
        self.calculate_btn.clicked.connect(self.start_calculation)
        input_layout.addWidget(self.calculate_btn)
        
        frame_layout.addLayout(input_layout)
        
        # 示例提示 (无边框)
        example_label = QLabel("示例: 123, -456, 1e3")
        example_label.setStyleSheet("color: #adb5bd; font-size: 12px;")
        frame_layout.addWidget(example_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #e9ecef;")
        frame_layout.addWidget(separator)
        
        # 结果区域 (无边框)
        result_title = QLabel("计算结果")
        result_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #343a40;")
        frame_layout.addWidget(result_title)
        
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        frame_layout.addWidget(self.result_display)
        
        main_layout.addWidget(main_frame)
        
        # 底部状态栏
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("color: #6c757d;")
        
        # 连接回车键
        self.input_field.returnPressed.connect(self.calculate_btn.click)
        
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
            self.status_bar.showMessage("正在计算...")
            
            # 创建工作线程
            self.worker = WorkerThread(target)
            self.worker.result_ready.connect(self.show_result)
            self.worker.error_occurred.connect(self.show_error)
            self.worker.finished.connect(self.cleanup_after_calculation)
            self.worker.start()
            
        except ValueError:
            self.result_display.setPlainText("错误: 请输入有效整数或科学计数法(如1e3)")
            self.status_bar.showMessage("输入错误")
            self.input_field.clear()
    
    def cleanup_after_calculation(self):
        """计算完成后清理输入框并恢复按钮状态"""
        self.input_field.clear()
        self.calculate_btn.setEnabled(True)
        self.input_field.setFocus()
    
    def show_result(self, target, expr, elapsed):
        if expr:
            # 设置彩色文本
            self.result_display.setHtml(f"""
                <div style="font-family: Consolas, 'Courier New', monospace; font-size: 14px;">
                    <p>目标: <span style="font-weight: bold;">{target}</span></p>
                    <p>结果 (<span style="color: #6c757d;">{elapsed:.2f}秒</span>):</p>
                    <p><span style="font-weight: bold;">{target}</span> = <span style="color: #4a90e2;">{expr}</span></p>
                    <p style="color: #0165cc; font-weight: bold;">⑨ baka~</p>
                </div>
            """)
            
            self.status_bar.showMessage(f"计算完成 - 耗时 {elapsed:.2f}秒")
            
            # 播放声音
            finder = ImprovedNineExpressionFinder()
            finder.play_baka_sound()
        else:
            self.result_display.setPlainText(f"无法找到 {target} 的有效表达式")
            self.status_bar.showMessage("未找到结果")
    
    def show_error(self, error_msg):
        self.result_display.setPlainText(f"错误: {error_msg}")
        self.status_bar.showMessage("发生错误")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序字体
    font = QFont()
    font.setFamily("Microsoft YaHei" if sys.platform == "win32" else "PingFang SC")
    app.setFont(font)
    
    window = NineSolverGUI()
    window.show()
    sys.exit(app.exec())