# coding=utf-8
import sys
import traceback
import Configuration
import pygame
import Base
from Enemy import Enemy
from Player import Player
from Controller import GroupManager


class GameScreen:
    def __init__(self, root=None, size=Configuration.ScreenSize, background=Configuration.BackGround, fps=60):
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.size = size
        self.background = background
        self.manager = None
        self.root = root
        self.frame = Base.MyFrame(self.size, self.root)
        self.textframe = Base.MyFrame(self.size, self.root, alpha=102)
        self.running = False
        self.caption = f'Escape_Rect Version:{Configuration.Version}'
        self.enemy_num = 1
        self.font = None
        self.boardColor = (20, 20, 20)  # 边框颜色
        self.fontcolor = (255, 0, 0)
        self.livescolor = (255, 255, 0)
        self.fontsize = 30
        self.cdweight = 3  # cd条宽
        self.cdcolor = 0x1A, 0xE6, 0xE6  # cd条颜色

    def gameloop(self):
        def countEscapeTimes():
            totalEscapeTimes = 0
            for enemy in enemies:
                totalEscapeTimes += enemy.movetimes
            return totalEscapeTimes

        enemies = []
        pygame.init()
        moveper = 0
        iswinning = False
        self.running = True
        self.manager = GroupManager(self.frame)
        pygame.display.set_caption(self.caption)
        try:
            Myfont = pygame.font.Font(self.font, self.fontsize)
        except Exception as e:
            print(type(e), e)
            Myfont = pygame.font.Font(None, self.fontsize)
        sw, sh = self.frame.get_rect().size
        playersize = (sw + sh) / 2 // 40
        player = Player(self.frame, playersize, playersize)
        self.manager.setplayer(player)
        try:
            enemysize = 20  # 敌人大小，数值越大敌人越小
            screensize = (sw + sh) // 2
            # 创建敌人
            for i in range(self.enemy_num):
                enemy = Enemy(self.frame, screensize / enemysize, screensize / enemysize)
                self.manager.add(enemy)
                enemies.append(enemy)

            while self.running:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.close()
                            return
                        if event.key == pygame.K_TAB:
                            Base.setting()
                    if event.type == pygame.QUIT:
                        self.close()
                        return
                if player.check(self.manager.sprites()):  # 检查玩家是否死亡
                    self.close()
                    return

                # 显示边框
                pygame.draw.rect(self.frame, self.boardColor, [0, 0, *self.size], 1)
                # 摆放技能CD
                restpercent = max((player.lastSkillTime + player.skillSleepingTime - Base.getTimeMil()) /
                                  player.skillSleepingTime, 0)  # CD剩余百分比
                cdRect = (-1, int(sh / 2), int(sw * restpercent), self.cdweight)
                pygame.draw.rect(self.frame, self.cdcolor, cdRect)

                # 摆放玩家血量
                livesmessage = ' '.join(["■"] * player.lives)
                textlives = Myfont.render(livesmessage, True, self.livescolor)
                w, h = textlives.get_rect().size
                self.frame.blit(textlives, (int(sw / 2 - w / 2), int(sh / 2 - h / 2)))

                # 更新敌人和玩家状态
                moveper, iswinning = self.manager.update(events)
                if iswinning:
                    raise Exception("Winning!")

                # 摆放顶部文字
                text1 = Myfont.render(
                    f'Static:{Base.getTimeSec() - self.manager.playerlastmovetime / 1000:.2f} Enemies:{self.enemy_num} Escapes:{countEscapeTimes()} Second:{Base.getTimeSec():.1f} MovePer:{moveper:.2f}',
                    True, self.fontcolor)
                w, h = text1.get_rect().size
                sizeratio = w / sw
                text1after = pygame.transform.scale(text1, (int(sw), int(h / sizeratio)))
                aw = text1after.get_rect().width
                ah = text1after.get_rect().height
                self.textframe = self.textframe.clearResize(h=ah)
                self.textframe.blit(text1after, (int(sw / 2 - aw / 2), 0))

                # 刷新页面
                self.update(player.rect.topleft)
                self.clock.tick(self.fps)
                Base.addTime()
        finally:
            traceback.print_exc(file=sys.stderr)
            self.close()
            return Base.getTimeSec(), countEscapeTimes(), moveper, player.olives, iswinning

    def update(self, playerPos=None):  # 只有在RelShowing成立时，playerPos才会起作用
        pygame.display.update()
        self.root.fill(self.background)

        # 更新Frame
        if Configuration.RelShowing and playerPos:
            pos = [-i for i in playerPos]
            pos[0] += Configuration.SW // 2
            pos[1] += Configuration.SH // 2
            self.frame.print(pos)
        else:
            self.frame.print()
        # 更新文字Frame
        self.textframe.print()

        self.textframe.fill(self.background)
        self.frame.fill(self.background)

    def close(self):
        self.running = False
        Base.clearTime()


def main():
    s = GameScreen((500, 200), fps=60)
    s.gameloop()
    pygame.quit()


if __name__ == '__main__':
    main()
