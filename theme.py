# -*- coding: utf-8 -*-
'''
StandardRobot++ Tool 深色主题
统一颜色 / 字体 / 控件工厂
'''

BG        = "#101319"   # 窗口底色
CARD      = "#181d25"   # 卡片底色
CARD_HI   = "#222a35"   # 控件底色
BORDER    = "#2b3542"   # 边框
FG        = "#e9edf3"   # 主文字
FG_DIM    = "#8b95a7"   # 次要文字
ACCENT    = "#3da9fc"   # 主题蓝
ACCENT_DK = "#2f86cf"
OK        = "#2dd4a7"   # 绿
WARN      = "#f4c542"   # 黄
ERR       = "#f2555a"   # 红

FONT        = "Microsoft YaHei UI"
FONT_TXT    = (FONT, 10)
FONT_SM     = (FONT, 9)
FONT_BOLD   = (FONT, 10, "bold")
FONT_TITLE  = (FONT, 11, "bold")
FONT_MONO   = ("Consolas", 13)
FONT_MONO_B = ("Consolas", 16, "bold")

# 波形图曲线颜色循环
LINE_COLORS = ["#3da9fc", "#2dd4a7", "#f4c542", "#f2555a",
               "#b197fc", "#ff922b", "#63e6be", "#ff8787"]


def apply(root):
    '''全局应用深色主题'''
    import tkinter.ttk as ttk
    root.configure(bg=BG)

    # Combobox 下拉列表(原生 listbox)配色
    root.option_add("*TCombobox*Listbox.background", CARD_HI)
    root.option_add("*TCombobox*Listbox.foreground", FG)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
    root.option_add("*TCombobox*Listbox.font", FONT_TXT)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "Dark.TCombobox",
        fieldbackground=CARD_HI, background=CARD_HI, foreground=FG,
        arrowcolor=FG_DIM, bordercolor=BORDER, lightcolor=BORDER,
        darkcolor=BORDER, insertcolor=FG, padding=4,
        selectbackground=CARD_HI, selectforeground=FG, font=FONT_TXT,
    )
    style.map(
        "Dark.TCombobox",
        fieldbackground=[("readonly", CARD_HI)],
        foreground=[("readonly", FG)],
        background=[("readonly", CARD_HI)],
    )
    style.configure(
        "Dark.Vertical.TScrollbar",
        background=CARD_HI, troughcolor=CARD, bordercolor=CARD,
        arrowcolor=FG_DIM,
    )
    return style


def card(parent, title=None, **kwargs):
    '''深色卡片(带左上角标题)'''
    import tkinter as tk
    return tk.LabelFrame(
        parent,
        text=(" " + title + " ") if title else "",
        bg=CARD, fg=FG_DIM, font=FONT_SM, bd=0,
        highlightthickness=1, highlightbackground=BORDER,
        labelanchor="nw", **kwargs
    )


def button(parent, text, command=None, accent=False, **kwargs):
    '''扁平按钮(带悬浮变色)'''
    import tkinter as tk
    bg = ACCENT if accent else CARD_HI
    b = tk.Button(
        parent, text=text, command=command, bg=bg, fg="#ffffff" if accent else FG,
        activebackground=ACCENT_DK if accent else BORDER,
        activeforeground="#ffffff", relief="flat", bd=0,
        font=FONT_TXT, cursor="hand2", padx=14, pady=5,
        highlightthickness=0, **kwargs
    )

    def on_enter(_):
        b.configure(bg=ACCENT_DK if accent else BORDER)

    def on_leave(_):
        b.configure(bg=ACCENT if accent else CARD_HI)

    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)
    return b


def label(parent, text, dim=False, bold=False, mono=False, font=None, **kwargs):
    '''统一风格的标签'''
    import tkinter as tk
    if font is None:
        if mono:
            font = FONT_MONO_B if bold else FONT_MONO
        else:
            font = FONT_BOLD if bold else FONT_TXT
    return tk.Label(parent, text=text, bg=kwargs.pop("bg", CARD),
                    fg=FG_DIM if dim else FG, font=font, **kwargs)
