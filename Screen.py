# coding = utf-8
import sys
import time
import traceback

import pygame
from Enemy import Enemy
from Player import Player
from Controller import GroupManager


class GameScreen:
    def __init__(self, screensize, background=(0, 0, 0), fps=60, version='None'):
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.version = version
        self.size = screensize
        self.background = background
        self.manager = None
        self.screen = None
        self.running = False
        self.caption = f'Escape_Rect Version:{version}'
        self.enemy_num = 1
        self.distanse = 50
        self.font = None
        self.fontcolor = (255, 0, 0)
        self.livescolor = (255, 255, 0)
        self.fontsize = 30
        self.nowtime = 0
        self.cdweight = 3  # cd条宽
        self.cdcolor = 0x1A, 0xE6, 0xE6  # cd条颜色

    def gameloop(self, screen=None):
        def counttimes():
            totalEscapeTimes = 0
            for enemy in enemies:
                totalEscapeTimes += enemy.movetimes
            return totalEscapeTimes

        enemies = []
        pygame.init()
        lasttime = time.time()
        nowfps = 0
        moveper = 0
        iswinning = False
        self.running = True
        self.screen = screen or pygame.display.set_mode(self.size)
        if not screen:
            print('New screen')
        self.manager = GroupManager(self.screen)
        pygame.display.set_caption(self.caption)
        try:
            Myfont = pygame.font.Font(self.font, self.fontsize)
        except Exception as e:
            print(type(e), e)
            Myfont = pygame.font.Font(None, self.fontsize)
        sw, sh = self.screen.get_rect().size
        playersize = (sw + sh) / 2 // 40
        player = Player(self.screen, playersize, playersize)
        self.manager.setplayer(player)
        try:
            enemysize = 20  # 敌人大小，数值越大敌人越小
            screensize = (sw + sh) // 2
            # 创建敌人
            for i in range(self.enemy_num):
                enemy = Enemy(self.screen, screensize / enemysize, screensize / enemysize, distanse=self.distanse)
                self.manager.add(enemy)
                enemies.append(enemy)

            while self.running:
                nowtime = time.time()
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.close()
                            return
                    if event.type == pygame.QUIT:
                        self.close()
                        return
                if player.check(self.manager.sprites()):
                    self.close()
                    return

                # 摆放技能CD
                restpercent = max((player.lastskilltime + player.skillsleepingtime - nowtime) /
                                  player.skillsleepingtime, 0)  # CD剩余百分比
                cdRect = (-1, int(sh / 2), int(sw * restpercent), self.cdweight)
                pygame.draw.rect(self.screen, self.cdcolor, cdRect)

                # 摆放玩家血量
                livesmessage = ' '.join(["■"] * player.lives)
                textlives = Myfont.render(livesmessage, True, self.livescolor)
                w, h = textlives.get_rect().size
                self.screen.blit(textlives, (int(sw / 2 - w / 2), int(sh / 2 - h / 2)))

                # 更新敌人和玩家状态
                moveper, iswinning = self.manager.update(events)
                if iswinning:
                    raise Exception("Winning!")

                # 摆放顶部文字
                text1 = Myfont.render(
                    f'FPS:{nowfps} Static:{nowtime - self.manager.playerlastmovetime:.2f} Enemies:{self.enemy_num} Escapes:{counttimes()} Second:{self.nowtime / self.fps:.1f} MovePer:{moveper:.2f}',
                    True, self.fontcolor)
                w, h = text1.get_rect().size
                sizeratio = w / sw
                text1after = pygame.transform.scale(text1, (int(sw), int(h / sizeratio)))
                aw = text1after.get_rect().width
                self.screen.blit(text1after, (int(sw / 2 - aw / 2), 0))

                # 刷新页面
                self.update()
                self.clock.tick(self.fps)
                nowfps = int(1 / max((nowtime - lasttime), 0.00005))
                lasttime = nowtime
                self.nowtime += 1
        finally:
            traceback.print_exc(file=sys.stderr)
            return self.nowtime / self.fps, counttimes(), moveper, player.olives, iswinning

    def update(self):
        pygame.display.update()
        self.screen.fill(self.background)

    def close(self):
        self.running = False


def main():
    s = GameScreen((500, 200), fps=60, version='alpha')
    s.gameloop()
    pygame.quit()


if __name__ == '__main__':
    main()
