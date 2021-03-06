# coding=utf-8
from src.Basic.Base import *
import src.Basic.Base as Base
from src.GameControl.Controller import GroupManager
from src.Interaction.Screen import GameScreen
from random import randint
from src.Interaction.ProgressDrawer import Loader

pygame.init()


class UserFacer:
    version = Configuration.Version

    def __init__(self):
        clearTime()
        Base.CurrentUserFacer = self
        self.clock = pygame.time.Clock()
        self.root = None
        self.size = self.startSize = Configuration.ScreenSize
        self.minSize = Configuration.MinSize
        self.fps = Configuration.FPS  # 更改会使游戏失常
        self.fontSize = lambda: int(self.root.get_rect().width // Con.FontRelation)  # 根据屏幕大小更改字体大小
        self.defaultFontSize = 20
        # noinspection PyTypeChecker
        self.Font: pygame.font.Font = getFont(Con.Font, self.defaultFontSize)
        self.fontColor = Configuration.FontColor
        self.background = Configuration.BackGround
        self.running = False
        self.playerNum = 1
        self.min_enemy_num = Configuration.LeastEnemy  # 最小敌人数
        self.max_enemy_num = Configuration.MostEnemy  # 最大敌人数
        self.last_enemy_num = 0  # 可忽视
        self.settingKey = [pygame.K_TAB]
        self.startKey = [pygame.K_RETURN, pygame.K_r]
        self.quitKey = [pygame.K_ESCAPE, pygame.K_q]
        self.fullKey = [pygame.K_F11]
        self.upPlayerKey = [pygame.K_UP]
        self.downPlayerKey = [pygame.K_DOWN]
        Configuration.ButtonSize = (self.size[0] + self.size[1]) // 2 // 6
        self.clickRect = pygame.Rect(
            [0, int(self.size[1] - 0.06 * self.size[1]), self.size[0], int(0.06 * self.size[1])])  # 点击开始游戏区域
        self.settingClickRect = pygame.Rect([0, 0, 80, 20])  # 点击设置区域

    def resize(self, size, *args):
        self.root = pygame.display.set_mode(size, *args)
        self.size = Configuration.SW, Configuration.SH = Configuration.ScreenSize = size
        Configuration.ButtonSize = (size[0]) // 6
        Configuration.ButtonMargin = size[0] // 20
        self.Font = getFont(Con.Font, self.fontSize())

    def startingAnimation(self):
        loader = Loader(self.root, int(min(self.size) * 0.5), CENTER_POSITION, twoPoint=True)
        lastingTime = 500
        startTime = getTimeMil()
        while lastingTime + startTime >= getTimeMil():
            nowTime = getTimeMil()
            loader.percent = 1 - (lastingTime + startTime - nowTime) / lastingTime
            loader.flush()
            self.update()
        pygame.event.clear()

    def update(self):
        pygame.display.update()
        self.root.fill(self.background)
        self.clock.tick(self.fps)
        addTime()

    def increasePlayer(self, x):
        self.playerNum = max(self.playerNum + x, 1)

    def showMenu(self, time, escapetimes, process, lives, first, situation):
        self.running = True
        self.root = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.resize(self.root.get_size(), pygame.RESIZABLE)
        pygame.display.set_caption(f'Escape_Rect Version:{self.version}' + ('' if first else '——You Lost.'))
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if self.clickRect.x < x < self.clickRect.right:
                        if self.clickRect.y < y < self.clickRect.bottom:
                            self.startPlaying()
                            return True
                    if self.settingClickRect.x < x < self.settingClickRect.right:
                        if self.settingClickRect.y < y < self.settingClickRect.bottom:
                            self.setting()
                if event.type == pygame.KEYDOWN:
                    if event.key in self.settingKey:
                        self.setting()
                    if event.key in self.startKey:
                        self.startPlaying()
                        return True
                    if event.key in self.quitKey:
                        self.close()
                        return False
                    if event.key in self.fullKey:
                        self.fullScreen()
                    if event.key in self.upPlayerKey:
                        self.increasePlayer(1)
                    if event.key in self.downPlayerKey:
                        self.increasePlayer(-1)
                if event.type == pygame.VIDEORESIZE:
                    if Con.FullScreen:  # 全屏不缩放
                        continue
                    if self.size[0] != event.size[0]:  # 横坐标改变
                        width = event.size[0]
                        height = int(event.size[0] / Configuration.ScreenSizeRatio)
                    else:  # 纵坐标改变
                        height = event.size[1]
                        width = int(event.size[1] * Configuration.ScreenSizeRatio)
                    size = max(width, self.minSize[0]), max(height, self.minSize[1])
                    self.resize(size, pygame.RESIZABLE)
            mouseposx, mouseposy = pygame.mouse.get_pos()
            sw, sh = self.root.get_rect().size

            pygame.draw.rect(self.root, (255, 0, 0), self.clickRect)
            # 设置按钮文字
            settingText = self.Font.render('Setting', True, self.fontColor)
            self.root.blit(settingText, (0, 0))
            self.settingClickRect = settingText.get_rect()

            # 摆放文字
            otext1 = self.Font.render(
                f'Escape_Rect Version:{self.version}——Author:azazo1' if first else f'Enemies:{self.last_enemy_num} Seconds:{time:.2f} Size:{self.startSize}',
                True, self.fontColor)
            w, h = otext1.get_rect().size
            text1pos = (int(sw / 2 - w / 2), int(sh / 2 - h / 2))  # 固定式摆法
            self.root.blit(otext1, text1pos)

            # 摆放文字
            otext2 = self.Font.render(
                '' if first else f'EscapeTimes:{escapetimes} Process:{process:.2%} Lives:{lives}',
                True, self.fontColor)
            w, h = otext2.get_rect().size
            if w > 1 and h > 1:
                text2pos = (int(sw / 2 - w / 2), int(sh / 2 - h / 2 + otext1.get_rect().height))  # 固定式摆法
                self.root.blit(otext2, text2pos)

            # 摆放底部文字
            textbottom = self.Font.render(
                {
                    LOST: "You Lost...",
                    WIN: "You Win!",
                    RUNNING: "",
                    RESTING: "[RETURN] START, [TAB] SETTING",
                }[situation] + f' PlayerNum:{self.playerNum}',
                True, self.fontColor
            )
            w, h = textbottom.get_rect().size
            textbottommovedistansex = sw - w
            textbottompos = (int(textbottommovedistansex * mouseposx / sw), sh - textbottom.get_rect().height)  # 浮动式摆法
            self.root.blit(textbottom, textbottompos)
            self.clickRect = pygame.Rect(*textbottompos, *textbottom.get_rect().size)
            self.update()

    def close(self):
        self.running = False

    def quit(self):
        pygame.quit()
        self.close()

    def go(self):
        first = 1
        runningTime = 0
        escapeTimes = 0
        process = 0
        lives = 0
        situation = RESTING
        while 1:
            if not self.showMenu(runningTime, escapeTimes, process, lives, first=first, situation=situation):
                break
            first = 0
            game = GameScreen(self.root, self.size, fps=self.fps, fullScreen=Con.FullScreen)
            game.enemy_num = self.last_enemy_num = randint(self.min_enemy_num, self.max_enemy_num)
            game.Font = self.Font
            game.fontcolor = self.fontColor
            runningTime, escapeTimes, process, lives, situation = game.gameloop(self.playerNum)
            pass

    def fullScreen(self):
        if self.running:
            Con.FullScreen = not Con.FullScreen
            if Con.FullScreen:
                csize = pygame.display.list_modes()[0]
                self.resize(csize, pygame.FULLSCREEN)
            else:
                self.resize(Configuration.MinSize, pygame.RESIZABLE)

    def setting(self):
        self.resize(self.root.get_size(), pygame.RESIZABLE)  # 防止退出全屏卡住游戏
        Base.Setting()
        self.resize(pygame.display.list_modes()[0] if Con.FullScreen else self.root.get_size(),
                    # 重新进入全屏
                    pygame.FULLSCREEN if Con.FullScreen else pygame.RESIZABLE)

    def startPlaying(self):
        self.resize(self.root.get_size(),
                    pygame.FULLSCREEN if Con.FullScreen else 0)  # 开始游戏，将窗口设置为不可变换大小
        self.startSize = self.size
        self.startingAnimation()
        self.close()


if __name__ == '__main__':
    u = UserFacer()
    u.go()
    u.quit()
