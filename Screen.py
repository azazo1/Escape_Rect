# coding=utf-8
import random
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
        Base.clearTime()  # 重置游戏计时
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.size = size
        self.background = background
        self.manager = None
        self.root = root
        self.frame = Base.MyFrame(self.root, self.size)
        self.textFrame = Base.MyFrame(self.root, self.size, alpha=200)
        self.buttonFrame = Base.MyFrame(self.root,
                                        (self.size[0], Configuration.ButtonSize + 2 * Configuration.ButtonMargin),
                                        (0,
                                         self.root.get_rect().height - Configuration.ButtonSize - 2 * Configuration.ButtonMargin),
                                        alpha=70)
        [Base.Button(self.buttonFrame, c) for c in range(4)]  # 创建按钮
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

        playerSize = (sw + sh) / 2 // 40
        moveSpeed = int(sw / 70)  # 根据屏幕宽度调整移动速度
        player = Player(self.frame, playerSize, playerSize)
        player.moveSpeed = moveSpeed

        self.manager.buttons.extend(self.buttonFrame.children)
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

                # 摆放技能CD
                restPercent = max((player.lastSkillTime + player.skillSleepingTime - Base.getTimeMil()) /
                                  player.skillSleepingTime, 0)  if not Configuration.NoCD else 0# CD剩余百分比
                cdRect = (-1, int(sh / 2), int(sw * restPercent), self.cdweight)
                pygame.draw.rect(self.frame, self.cdcolor, cdRect)

                # 摆放可冲刺时效果
                nowTime = Base.getTimeMil()
                restPercent = (player.rushSleepTime + player.lastRushTime - nowTime) / player.rushSleepTime - Configuration.NoCD
                    # restPercent为剩余百分比，NoCD成立则始终小于零
                r = 10
                if restPercent < 0:
                    r = random.randint(0, r + 5) if Configuration.ParticlesShowing else r + 5
                else:
                    r = (1 - restPercent) * r
                pygame.draw.circle(self.root, self.cdcolor, pygame.mouse.get_pos(), r)

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
                self.textFrame = self.textFrame.clearResize(h=ah)
                self.textFrame.blit(text1after, (int(sw / 2 - aw / 2), 0))

                # 显示边框
                pygame.draw.rect(self.frame, self.boardColor, [0, 0, *self.size], 1)

                # 刷新页面
                self.refresh(player.rect.topleft)
                self.clock.tick(self.fps)
                Base.addTime()
        finally:
            traceback.print_exc(file=sys.stderr)
            self.close()
            return Base.getTimeSec(), countEscapeTimes(), moveper, player.olives, iswinning

    def refresh(self, playerPos=None):  # 只有在RelShowing成立时，playerPos才会起作用
        pygame.display.update()
        self.root.fill(self.background)

        # 更新Frame
        if Configuration.RelShowing and playerPos:
            pos = [-i for i in playerPos]
            pos[0] += Configuration.SW // 2
            pos[1] += Configuration.SH // 2
            self.frame.print(pos)
        else:
            self.frame.print((0, 0))
        # 更新文字Frame
        self.textFrame.print()
        # 更新按钮Frame
        if Configuration.ButtonShowing:
            self.buttonFrame.printChildren()
            self.buttonFrame.print()

        self.buttonFrame.fill(self.background)
        self.textFrame.fill(self.background)
        self.frame.fill(self.background)

    def close(self):
        self.running = False


def main():
    s = GameScreen((500, 200), fps=60)
    s.gameloop()
    pygame.quit()


if __name__ == '__main__':
    main()
