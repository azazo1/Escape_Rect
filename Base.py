# coding=utf-8
import pygame
import tkinter as tk
import pygame.font as pf
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
    buttonShowingButton = tk.Checkbutton(window, text='显示控制按钮', onvalue=True, offvalue=False,
                                         variable=buttonShowing)
    enemySleepTimeShowingButton = tk.Checkbutton(window, text='显示每个敌人移动间隙（毫秒）', onvalue=True, offvalue=False,
                                                 variable=enemySleepTimeShowing)
    confirmButton = tk.Button(window, text='确认', command=confirm)

    relShowingButton.pack()
    enemySleepTimeShowingButton.pack()
    buttonShowingButton.pack()
    confirmButton.pack()
    window.mainloop()


class MyWidget(pygame.Surface):
    def __init__(self, parent, size, pos=(0, 0), alpha=None):
        super(MyWidget, self).__init__(size)
        self.parent: MyFrame = parent
        self.size = self.w, self.h = size
        self.pos = self.x, self.y = pos
        self.set_alpha(alpha)
        self.alpha = alpha

    def print(self):
        self.parent.blit(self, self.pos)


class MyFrame(MyWidget):

    def __init__(self, parent: MyWidget, size: tuple, pos=(0, 0), alpha=None):
        super(MyFrame, self).__init__(parent, size, pos, alpha)
        self.fill(Configuration.BackGround)
        self.children = []

    def addChild(self, obj: MyWidget):
        obj.parent = self
        self.children.append(obj)

    def addChildren(self, objs: list):
        for i in objs:
            self.addChild(i)

    def printChildren(self):
        for i in self.children:
            i.print()

    def print(self, pos=None):
        if pos:
            self.pos = pos
        self.parent.blit(self, self.pos)

    def clearResize(self, w=None, h=None):
        result = MyFrame(self.parent, (w if w else self.size[0], h if h else self.size[1]), self.pos,
                         self.alpha)
        return result


class Button(MyWidget):

    def __init__(self, parent: MyFrame, command: int):
        """
        :param command: 按钮功能，左移：0，右移：1，跳跃：2，技能：3.
        """

        super(Button, self).__init__(parent, (Configuration.ButtonSize, Configuration.ButtonSize),
                                     (0, 0))
        self.parent.children.append(self)
        self.command = command
        self.margin = Configuration.ButtonMargin
        # 放置位置
        w, h = self.parent.get_size()
        self.positions = [
            (self.margin, self.margin),
            (self.margin + self.w + self.margin * 2, self.margin),
            (w - self.w * 2 - self.margin * 3, self.margin),
            (w - self.margin - self.w, self.margin)
        ]
        self.pos = self.x, self.y = self.positions[self.command]
        # 画背景，边框，填充
        self.fill(Configuration.BackGround)  # 初始背景
        pygame.draw.circle(self, Configuration.ButtonColor, [i // 2 for i in self.size],
                           Configuration.ButtonSize // 2)  # 按钮填充
        pygame.draw.circle(self, Configuration.ButtonBorderColor, [i // 2 for i in self.size],
                           Configuration.ButtonSize // 2, 3)  # 按钮边框
        # 摆放按钮图标
        self.font = pygame.font.Font(Configuration.Font, 15)
        self.icon = self.font.render('←→↑#'[self.command], True, Configuration.FontColor)
        iw, ih = self.icon.get_size()
        iconPos = self.w // 2 - iw // 2, self.h // 2 - ih // 2
        self.blit(self.icon, iconPos)

    def setParent(self, parent: MyFrame):
        self.parent.children.append(self)
        self.parent = parent

    def checkPressed(self):
        if not Configuration.ButtonShowing:
            return
        if pygame.mouse.get_pressed()[0]:
            return self.checkOver()

    def checkOver(self):  # 检查鼠标是否悬在按钮上
        MouseX, MouseY = tuple(pygame.mouse.get_pos())
        absX, absY = [a + b + Configuration.ButtonSize // 2 for a, b in zip(self.parent.pos, self.pos)]  # 按钮的中间位置
        if (MouseX - absX) ** 2 + (MouseY - absY) ** 2 <= (Configuration.ButtonSize // 2) ** 2:
            return True

    def print(self):
        self.parent.blit(self, self.pos)
