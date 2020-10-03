# coding=utf-8

from Screen import GameScreen
import tkinter as tk
import pygame
from random import randint

pygame.init()


class UserFacer:
    version = '0.45.3'

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.root = None
        self.size = self.osize = 700, 400
        self.fps = 60  # 更改会使游戏失常
        self.font = r'C:\Windows\Fonts\Consola.ttf'
        self.fontsize = 20
        self.fontcolor = (255, 0, 0)
        self.background = (0, 0, 0)
        self.running = False
        self.min_enemy_num = 1  # 最小敌人数
        self.max_enemy_num = 5  # 最大敌人数
        self.last_enemy_num = 0  # 可忽视
        self.min_distanse = 100
        self.max_distanse = 200
        self.last_distanse = 0  # 可忽视
        self.resizekey = [pygame.K_TAB]
        self.startkey = [pygame.K_RETURN, pygame.K_r]
        self.quitkey = [pygame.K_ESCAPE, pygame.K_q, 48]

    def showstart(self, time, escapetimes, moveper, lives, first, win=False):
        self.running = True
        size = self.size
        pygame.font.init()
        try:
            Myfont = pygame.font.Font(self.font, self.fontsize)
        except Exception as e:
            print(type(e), e)
            Myfont = pygame.font.Font(None, self.fontsize)
        self.root = root = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        pygame.display.set_caption(f'Escape_Rect Version:{self.version}' + ('' if first else '——You Lost.'))
        clickrect = self.root.get_rect()

        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if clickrect.x < x < clickrect.right:
                        if clickrect.y < y < clickrect.bottom:
                            return True
                if event.type == pygame.KEYDOWN:
                    if event.key in self.resizekey:
                        self.root = root = pygame.display.set_mode(self.osize, pygame.RESIZABLE)
                    if event.key in self.startkey:
                        self.close()
                        return True
                    if event.key in self.quitkey:
                        self.close()
                        return False
                if event.type == pygame.VIDEORESIZE:
                    self.root = root = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    self.size = event.size
            mouseposx, mouseposy = pygame.mouse.get_pos()
            sw, sh = root.get_rect().size
            # 摆放文字
            otext1 = Myfont.render(
                f'Escape_Rect Version:{self.version}——Author:azazo1' if first else f'Enemies:{self.last_enemy_num} Seconds:{time:.2f} Size:{size}',
                True, self.fontcolor)
            ow, oh = otext1.get_rect().size
            text1size = int(sw / 2), int(sw / 2 / ow * oh)
            text1 = pygame.transform.scale(otext1, text1size)
            w, h = text1.get_rect().size
            text1pos = (int(sw / 2 - w / 2), int(sh / 2 - h / 2))  # 固定式摆法
            root.blit(text1, text1pos)

            # 摆放文字
            otext2 = Myfont.render(
                '' if first else f'EscapeTimes:{escapetimes} Moveper:{moveper:.2f} Lives:{lives}',
                True, self.fontcolor)
            ow, oh = otext2.get_rect().size
            if ow - 1:
                text2size = int(sw / 2), int(sw / 2 / ow * oh)
                text2 = pygame.transform.scale(otext2, text2size)
                w, h = text2.get_rect().size
                text2pos = (int(sw / 2 - w / 2), int(sh / 2 - h / 2 + text1.get_rect().height))  # 固定式摆法
                root.blit(text2, text2pos)

            textbottom = Myfont.render(['[R] or [RETURN] or [CLICK HERE] to START', "You Win!"][win],
                                       True, self.fontcolor)
            w, h = textbottom.get_rect().size
            textbottommovedistansex = sw - w
            textbottommovedistansey = sh - h
            textbottompos = (int(textbottommovedistansex * mouseposx / sw), sh - textbottom.get_rect().height)  # 浮动式摆法
            # textbottompos = (int(sw / 2 - w / 2), sh)#固定式摆法
            root.blit(textbottom, textbottompos)
            clickrect = pygame.Rect(*textbottompos, *textbottom.get_rect().size)

            pygame.display.update()
            root.fill(self.background)
            self.clock.tick(self.fps)

    def close(self):
        self.running = False

    def quit(self):
        pygame.quit()
        self.running = False

    def go(self):
        first = 1
        time = 0
        escapetimes = 0
        moveper = 0
        lives = 0
        iswinning = False
        while 1:
            if not self.showstart(time, escapetimes, moveper, lives, first=first, win=iswinning):
                break
            first = 0
            game = GameScreen(self.size, fps=self.fps, version=self.version)
            game.enemy_num = self.last_enemy_num = randint(self.min_enemy_num, self.max_enemy_num)
            game.distanse = self.last_distanse = randint(self.min_distanse, self.max_distanse)
            game.font = self.font
            game.fontcolor = self.fontcolor
            game.fontsize = self.fontsize
            time, escapetimes, moveper, lives, iswinning = game.gameloop(self.root)


if __name__ == '__main__':
    UserFacer().go()
    pygame.quit()
