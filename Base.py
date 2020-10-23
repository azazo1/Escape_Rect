# coding=utf-8
import pygame
import tkinter as tk

import Configuration

freshedPages = [0]  # 用已显示帧数返回时间


def addTime():
    freshedPages[0] += 1


def clearTime():
    freshedPages[0] = 0


def getTimeMil():  # 返回时间 毫秒
    return int(freshedPages[0] / Configuration.FPS * 1000)


def getTimeSec():  # 返回时间 秒
    return freshedPages[0] / Configuration.FPS


def setting():
    def confirm():
        Configuration.RelShowing = relShowing.get()
        Configuration.ButtonShowing = buttonShowing.get()
        Configuration.EnemySleepTimeShowing = enemySleepTimeShowing.get()
        window.destroy()

    window = tk.Tk()
    window.title('设置')
    window.geometry(f'{Configuration.MinSize[0]}x{Configuration.MinSize[1]}+10+10')

    relShowing = tk.BooleanVar()
    relShowing.set(Configuration.RelShowing)
    buttonShowing = tk.BooleanVar()
    buttonShowing.set(Configuration.ButtonShowing)
    enemySleepTimeShowing = tk.BooleanVar()
    enemySleepTimeShowing.set(Configuration.EnemySleepTimeShowing)

    relShowingButton = tk.Checkbutton(window, text='视角随角色移动', onvalue=True, offvalue=False, variable=relShowing)
    buttonShowingButton = tk.Checkbutton(window, text='显示按钮(暂未实现)', onvalue=True, offvalue=False,
                                         variable=buttonShowing)
    enemySleepTimeShowingButton = tk.Checkbutton(window, text='显示每个敌人移动间隙（毫秒）', onvalue=True, offvalue=False,
                                                 variable=enemySleepTimeShowing)
    confirmButton = tk.Button(window, text='确认', command=confirm)

    relShowingButton.pack()
    enemySleepTimeShowingButton.pack()
    buttonShowingButton.pack()
    confirmButton.pack()
    window.mainloop()


class MyFrame(pygame.Surface):

    def __init__(self, size, parent: pygame.Surface, alpha=None):
        super(MyFrame, self).__init__(size)
        self.fill(Configuration.BackGround)
        self.set_alpha(alpha)
        self.size = size
        self.parent = parent
        self.alpha = alpha

    def print(self, pos=(0, 0)):
        self.parent.blit(self, pos)

    def fillParent(self, color=(0, 0, 0)):
        self.parent.fill(color)

    def clearResize(self, w=None, h=None):
        result = MyFrame((w if w else self.size[0], h if h else self.size[1]),
                         self.parent,
                         self.alpha)
        return result
