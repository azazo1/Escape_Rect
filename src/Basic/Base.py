# coding=utf-8
import time
from platform import system
from typing import Optional
import pygame
from math import pi
import tkinter as tk
from src.Basic import Configuration

Con = Configuration
freshedPages = [0]  # 用已显示帧数返回时间
Con.ButtonShowing = system() != 'Windows'  # (Linux显示)

UserFacerOfNow = None


def addTime():
    freshedPages[0] += 1


def clearTime():
    freshedPages[0] = 0


def getTimeMilPerPage():
    return int((1 / Con.FPS) * 1000)


def getTimeMil():  # 返回时间 毫秒
    return int(freshedPages[0] / Con.FPS * 1000)


def getTimeSec():  # 返回时间 秒
    return freshedPages[0] / Con.FPS


def getFont(family, size):
    try:
        get = pygame.font.Font(family, size)
    except FileNotFoundError as e:
        print(e, family)
        Con.Font = None
        get = pygame.font.Font(None, int(size))
    return get


def getSound(path, volume=0.5):
    try:
        get = pygame.mixer.Sound(path)
        get.set_volume(volume)
        return get
    except FileNotFoundError as e:
        print(e, path)


def playSound(s: Optional[pygame.mixer.Sound]):
    try:
        s.play() if Con.IfSound else None
    except Exception:
        pass


def angleToFloat(angle):
    return angle * pi / 180


def printToCenter(target: pygame.Surface, src: pygame.Surface, deltaX=0, deltaY=0):
    """
    将src打印到target中心
    :param target:
    :param src:
    :param deltaX: X偏移量
    :param deltaY: Y偏移量
    :return:
    """
    w1, h1 = target.get_size()
    w2, h2 = src.get_size()
    pos = int(w1 / 2 - w2 / 2 + deltaX), int(h1 / 2 - h2 / 2 + deltaY)
    target.blit(src, pos)


class Setting:
    def __init__(self):
        self.bg = '#{:x}{:x}{:x}'.format(*Con.BackGround)
        self.window = tk.Tk()
        self.initVars()
        self.prepareWindow()
        self.mainloop()

    # noinspection PyAttributeOutsideInit
    def initVars(self):
        self.FullScreen = tk.BooleanVar()
        self.Invincible = tk.BooleanVar()
        self.ParticlesShowing = tk.BooleanVar()
        self.RelShowing = tk.BooleanVar()
        self.ButtonShowing = tk.BooleanVar()
        self.EnemySleepTimeShowing = tk.BooleanVar()
        self.NoCD = tk.BooleanVar()
        self.IfSound = tk.BooleanVar()

        self.FullScreen.set(Con.FullScreen)
        self.RelShowing.set(Con.RelShowing)
        self.ButtonShowing.set(Con.ButtonShowing)
        self.EnemySleepTimeShowing.set(Con.EnemySleepTimeShowing)
        self.ParticlesShowing.set(Con.ParticlesShowing)
        self.Invincible.set(Con.Invincible)
        self.NoCD.set(Con.NoCD)
        self.IfSound.set(Con.IfSound)
        self.advanceFeaturesVar = [self.NoCD, self.Invincible]  # 高级功能变量，注意要与Configuration中一致

    def __getattr__(self, item):
        return eval(f'self.{item}', locals())

    # noinspection PyAttributeOutsideInit
    def prepareWindow(self):
        self.window.title('设置')

        fullScreenButton = tk.Checkbutton(self.window, text='全屏', variable=self.FullScreen,
                                          command=UserFacerOfNow.fullScreen)
        invincibleButton = tk.Checkbutton(self.window, text='无敌', variable=self.Invincible)
        noCDButton = tk.Checkbutton(self.window, text='没有CD', variable=self.NoCD)
        buttonShowingButton = tk.Checkbutton(self.window, text='显示控制按钮', variable=self.ButtonShowing)
        relShowingButton = tk.Checkbutton(self.window, text='视角随角色移动', variable=self.RelShowing)
        particlesShowingButton = tk.Checkbutton(self.window, text='显示粒子与效果', variable=self.ParticlesShowing)
        enemySleepTimeShowingButton = tk.Checkbutton(self.window, text='显示每个敌人移动间隙和单次移动时间（毫秒）',
                                                     variable=self.EnemySleepTimeShowing)
        ifSoundButton = tk.Checkbutton(self.window, text='播放音效', variable=self.IfSound)
        confirmButton = tk.Button(self.window, text='确认', command=self.confirm)

        fullScreenButton.pack()
        invincibleButton.pack()
        noCDButton.pack()
        ifSoundButton.pack()
        buttonShowingButton.pack()
        relShowingButton.pack()
        particlesShowingButton.pack()
        enemySleepTimeShowingButton.pack()
        confirmButton.pack()

    def mainloop(self):
        self.window.mainloop()

    def destroy(self):
        self.window.destroy()

    def checkSame(self, *configurations):
        """判断参数中的变量（被选中）是否和Configuration中的变量完全一样"""
        for configuration in configurations:
            Conc = Con.getAttr(configuration)
            selfc = self.__getattr__(configuration).get()
            if Conc != selfc and selfc:
                return False  # 有不同且被选中
        return True  # 如果全相同则返回True

    def checkPasswordInput(self, ):
        """configurations: 要修改的Configuration模块中的变量，里面可以有None"""
        result = False

        def check():  # 检查密码
            nonlocal result
            if inputEntry.get() == Con.Password:
                result = True
                root.destroy()
                self.destroy()
            else:
                textLabel.configure(text='密码错误')
                textLabel.configure(bg='red')
                root.update()
                time.sleep(1)
                textLabel.configure(bg=self.bg,
                                    text='要想用高级功能，请输入密码')

        root = tk.Tk()
        root.title('输入密码')
        root.geometry(f'{Con.MinSize[0]}x{Con.MinSize[1]}+10+10')
        textLabel = tk.Label(root,
                             text='要想用高级功能，请输入密码',
                             bg=self.bg)
        textLabel.pack()
        inputEntry = tk.Entry(root, width=20, show='*')
        inputEntry.pack()
        tk.Button(root, text='确定', command=check).pack()
        root.mainloop()
        return result

    def confirm(self):  # 确认更改并要求输入密码
        if not self.checkSame(*Con.advanceFeatures):  # 判断是否需要输入密码
            if self.checkPasswordInput():  # 判断密码输入是否正确
                self.advanceSave()
                self.save()
            else:
                return  # 取消了密码输入，不保存任何
        else:
            self.advanceSave()
            self.save()
            self.destroy()

    def advanceSave(self):
        Con.Invincible = self.Invincible.get()
        Con.NoCD = self.NoCD.get()

    def save(self):
        # Con.FullScreen = self.FullScreen.get() # 全屏由UserFacer修改
        Con.EnemySleepTimeShowing = self.EnemySleepTimeShowing.get()
        Con.RelShowing = self.RelShowing.get()
        Con.ButtonShowing = self.ButtonShowing.get()
        Con.ParticlesShowing = self.ParticlesShowing.get()
        Con.IfSound = self.IfSound.get()


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
        self.fill(Con.BackGround)
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

        super(Button, self).__init__(parent, (Con.ButtonSize, Con.ButtonSize),
                                     (0, 0))
        self.parent.children.append(self)
        self.command = command
        self.margin = Con.ButtonMargin
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
        self.fill(Con.BackGround)  # 初始背景
        pygame.draw.circle(self, Con.ButtonColor, [i // 2 for i in self.size],
                           Con.ButtonSize // 2)  # 按钮填充
        pygame.draw.circle(self, Con.ButtonBorderColor, [i // 2 for i in self.size],
                           Con.ButtonSize // 2, 3)  # 按钮边框
        # 摆放按钮图标
        self.font = getFont(Con.Font, 15)
        self.icon = self.font.render('←→↑#'[self.command], True, Con.FontColor)
        iw, ih = self.icon.get_size()
        iconPos = self.w // 2 - iw // 2, self.h // 2 - ih // 2
        self.blit(self.icon, iconPos)

    def setParent(self, parent: MyFrame):
        self.parent.children.append(self)
        self.parent = parent

    def checkPressed(self):
        if not Con.ButtonShowing:
            return
        if pygame.mouse.get_pressed(3)[0]:
            return self.checkOver()

    def checkOver(self):  # 检查鼠标是否悬在按钮上
        MouseX, MouseY = tuple(pygame.mouse.get_pos())
        absX, absY = [a + b + Con.ButtonSize // 2 for a, b in zip(self.parent.pos, self.pos)]  # 按钮的中间位置
        if (MouseX - absX) ** 2 + (MouseY - absY) ** 2 <= (Con.ButtonSize // 2) ** 2:
            return True

    def print(self):
        self.parent.blit(self, self.pos)
