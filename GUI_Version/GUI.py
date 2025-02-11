import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread, Event
from queue import Queue


class NineSolverApp(tk.Tk):
    def __init__(self, finder):
        super().__init__()
        self.finder = finder  # 保存传入的 finder 实例
        self.finder.gui_app = self  # 建立双向引用
        self.search_stop_event = Event()
        self.result_queue = Queue()
        self.setup_ui()
        self.check_queue()
        self.retry_result = None  # 新增初始化
        self.gui_app = None  # 新增初始化
        self.gui_mode = True  # 新增标志位
        self.gui_app: NineSolverApp = None  # 添加类型注解
        self.bind("<<ShowRetryDialog>>", self.on_show_retry_dialog)

    def on_show_retry_dialog(self, event):
        self.retry_result = None
        self.retry_result = self.ask_retry()

    def ask_retry(self) -> bool:
        self.confirm_dialog = tk.Toplevel(self)
        # 添加结果变量
        self.retry_result = False  # 初始化默认值

        ttk.Label(self.confirm_dialog, text="是否解除时间限制重新尝试？").pack(padx=20, pady=10)

        btn_frame = ttk.Frame(self.confirm_dialog)
        btn_frame.pack(pady=10)

        def set_result(result: bool):
            self.retry_result = result
            self.confirm_dialog.destroy()

        ttk.Button(btn_frame, text="是", command=lambda: set_result(True)).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="否", command=lambda: set_result(False)).pack(side='left')

        self.confirm_dialog.transient(self)
        self.confirm_dialog.grab_set()
        self.wait_window(self.confirm_dialog)
        return self.retry_result

    def setup_ui(self):
        # Material You 风格配置
        self.configure(bg='#F3EDF7')
        style = ttk.Style()
        style.theme_create('material', parent='alt', settings={
            'TButton': {
                'configure': {
                    'padding': 10,
                    'background': '#6750A4',
                    'foreground': 'white',
                    'font': ('Segoe UI', 12)
                },
                'map': {
                    'background': [('active', '#7965AF')]
                }
            },
            'TEntry': {
                'configure': {
                    'fieldbackground': '#E7E0EC',
                    'foreground': '#1D1B20',
                    'font': ('Segoe UI', 14)
                }
            },
            'TLabel': {
                'configure': {
                    'background': '#F3EDF7',
                    'foreground': '#1D1B20',
                    'font': ('Segoe UI', 12)
                }
            }
        })
        style.theme_use('material')

        # 主界面布局
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill='both')

        # 输入区域
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='x', pady=10)

        ttk.Label(input_frame, text="目标整数:").pack(side='left')
        self.entry = ttk.Entry(input_frame, width=20)
        self.entry.pack(side='left', padx=10)
        self.entry.bind('<Return>', self.start_search)

        self.search_btn = ttk.Button(
            input_frame,
            text="求解",
            command=self.start_search
        )
        self.search_btn.pack(side='left')

        # 控制按钮区域
        self.control_frame = ttk.Frame(main_frame)
        self.stop_btn = ttk.Button(
            self.control_frame,
            text="中断搜索",
            command=self.stop_search,
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=5)

        # 结果展示区域
        self.output_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=10,
            font=('Segoe UI', 12),
            bg='#F3EDF7',
            fg='#1D1B20'
        )
        self.output_area.pack(expand=True, fill='both', pady=10)

    def start_search(self, event=None):
        try:
            target = int(self.entry.get())
            self.search_stop_event.clear()
            self.output_area.delete('1.0', tk.END)
            self.search_btn['state'] = 'disabled'
            self.stop_btn['state'] = 'normal'

            # 启动后台搜索线程
            Thread(target=self.run_search, args=(target,), daemon=True).start()
        except ValueError:
            self.show_message("错误：请输入有效整数！", 'red')

    def stop_search(self):
        self.search_stop_event.set()
        self.show_message("搜索已中断", '#B00020')

    # 修改NineSolverApp类的run_search方法
    def run_search(self, target):
        try:
            # 添加中断检查
            if self.search_stop_event.is_set():
                return

            # 修改后的搜索逻辑
            expr = self.finder.find_expression(target)
            # 使用after方法安全更新GUI
            self.after(0, lambda: self.result_queue.put(("result", expr)))

        except Exception as e:
            self.after(0, lambda: self.result_queue.put(("error", str(e))))
        finally:
            # 使用after确保线程安全
            self.after(0, self.enable_buttons)

    def enable_buttons(self):
        self.search_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')

    def check_queue(self) -> None:
        while not self.result_queue.empty():
            msg_type, content = self.result_queue.get()
            if msg_type == "result":
                self.show_result(content)
            elif msg_type == "error":
                self.show_message(content, '#B00020')
        self.after(100, lambda: self.check_queue())

    def show_result(self, expr):
        self.output_area.tag_config('baka', foreground='#0165CC')
        self.search_btn['state'] = 'normal'
        self.stop_btn['state'] = 'disabled'
        if "未找到" in expr:
            self.show_message(expr, '#B00020')
        else:
            self.output_area.insert(tk.END, f"结果：{expr}\n", 'success')
            self.output_area.insert(tk.END, "\033[38;2;1;101;204mbaka~\033[0m\n")
        self.output_area.insert(tk.END, "baka~\n", 'baka')  # 使用标签代替ANSI代码

    def show_message(self, message, color='#1D1B20'):
        self.output_area.tag_config('message', foreground=color)
        self.output_area.insert(tk.END, message + "\n", 'message')

    def _user_wants_to_abort(self) -> bool:
        # 修改为检查GUI事件标志
        return self.gui_app.search_stop_event.is_set()

    def find_expression(self, target: int) -> str:
        # 修改原有流程适配GUI
        result = self._find_expression_with_timeout(target)
        if result:
            return result

        # GUI专用确认流程
        self.gui_app.result_queue.put(("confirm", "是否解除时间限制重新尝试？"))
        # 等待用户确认（通过事件或队列实现）
        # 此处需要实现确认对话框的同步等待逻辑
        # 由于涉及GUI线程需要特殊处理（例如使用模态对话框）