import queue
import time
import tkinter as tk

import theme
from lib.log_info import LogInfo


class Page_Log(tk.Frame):
    '''运行日志页面（接收 LogInfo/LogWarning/LogError 输出）'''

    MAX_LINES = 2000

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.configure(bg=theme.BG)
        self.id = 5
        self.is_active = False
        self._queue = queue.Queue(maxsize=5000)
        self.auto_scroll = tk.BooleanVar(value=True)
        self.line_count = 0
        self.AddWidget()
        self._queue_poller()

    def AddWidget(self):
        toolbar = tk.Frame(self, bg=theme.BG)
        toolbar.pack(fill="x", padx=16, pady=(12, 6))

        theme.button(toolbar, text="清空日志", command=self.Clear).pack(side="left")
        tk.Checkbutton(toolbar, text="自动滚动", variable=self.auto_scroll,
                       bg=theme.BG, fg=theme.FG, activebackground=theme.BG,
                       activeforeground=theme.FG, selectcolor=theme.CARD_HI,
                       font=theme.FONT_TXT, highlightthickness=0, bd=0,
                       anchor="w").pack(side="left", padx=14)
        theme.label(toolbar, "日志会同时输出到控制台（如从控制台启动）",
                    dim=True, font=theme.FONT_SM, bg=theme.BG).pack(side="right")

        box = tk.Frame(self, bg=theme.CARD, highlightthickness=1,
                       highlightbackground=theme.BORDER)
        box.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.text = tk.Text(box, bg=theme.CARD, fg=theme.FG, bd=0, relief="flat",
                            font=("Consolas", 10), insertbackground=theme.FG,
                            wrap="none", highlightthickness=0, padx=10, pady=8)
        scrollbar = tk.Scrollbar(box, orient="vertical", command=self.text.yview,
                                 bg=theme.CARD_HI, troughcolor=theme.CARD,
                                 activebackground=theme.BORDER, bd=0,
                                 relief="flat", width=12, elementborderwidth=0,
                                 highlightthickness=0, highlightbackground=theme.CARD)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self.text.tag_configure("INFO", foreground=theme.FG)
        self.text.tag_configure("WARNING", foreground=theme.WARN)
        self.text.tag_configure("ERROR", foreground=theme.ERR)
        self.text.tag_configure("TIME", foreground=theme.FG_DIM)
        return

    ############################################################
    #  日志接收（线程安全）
    #  append_log 可由任意线程调用
    ############################################################
    def append_log(self, level:str, message:str) -> None:
        try:
            self._queue.put_nowait((level, message))
        except queue.Full:
            pass
        return

    def _queue_poller(self):
        drained = 0
        while drained < 200:
            try:
                level, message = self._queue.get_nowait()
            except queue.Empty:
                break
            timestamp = time.strftime("%H:%M:%S")
            self.text.insert("end", f"{timestamp} ", "TIME")
            self.text.insert("end", f"[{level}] {message}\n", level)
            self.line_count += 1
            drained += 1

        if self.line_count > self.MAX_LINES:
            self.text.delete("1.0", f"{self.line_count - self.MAX_LINES + 200}.0")
            self.line_count = self.MAX_LINES - 200

        if drained > 0 and self.auto_scroll.get():
            self.text.see("end")

        self.after(200, self._queue_poller)

    def Clear(self):
        self.text.delete("1.0", "end")
        self.line_count = 0
        LogInfo("日志已清空")
        return
