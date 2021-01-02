# coding=utf-8
import random
import sys
import traceback

from src.Basic.Base import *
from src.Char.Enemy import Enemy
from src.Char.Player import Player
from src.GameControl import Controller

Con = Configuration


class GameScreen:
    def __init__(self, root=None, size=Con.ScreenSize, background=Con.BackGround, fps=Con.FPS, fullScreen=False):
        clearTime()  # 重置游戏计时
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.size = size
        self.fullScreen = fullScreen
        self.background = background
        self.manager: Controller.GroupManager = None
        self.root = root
        self.frame = MyFrame(self.root, self.size)
        self.textFrame = MyFrame(self.root, self.size, alpha=200)
        self.buttonFrame = MyFrame(self.root,
                                   (self.size[0], Con.ButtonSize + 2 * Con.ButtonMargin),
                                   (0,
                                    self.root.get_rect().height - Con.ButtonSize - 2 * Con.ButtonMargin),
                                   alpha=70)
        [Button(self.buttonFrame, c) for c in range(4)]  # 创建按钮
        self.running = False
        self.caption = f'Escape_Rect Version:{Con.Version}'
        self.enemy_num = 1
        self.Font = None
        self.boardColor = (20, 20, 20)  # 边框颜色
        self.fontcolor = (0, 0, 0)
        self.livescolor = (255, 255, 0)
        self.fontsize = 30
        self.cdweight = 3  # cd条宽
        self.cdcolor = 0x1A, 0xE6, 0xE6  # cd条颜色

    def setting(self):
        self.root = pygame.display.set_mode(self.root.get_size())  # 防止退出全屏卡住游戏
        Setting()
        self.root = pygame.display.set_mode(self.root.get_size(),  # 重新进入全屏
                                            pygame.FULLSCREEN if self.fullScreen else 0)

    def gameloop(self):
        def countEscapeTimes():
            totalEscapeTimes = 0
            for enemy in enemies:
                totalEscapeTimes += enemy.movetimes
            return totalEscapeTimes

        enemies = []
        pygame.init()
        process = 0
        iswinning = False
        self.running = True
        self.manager = Controller.GroupManager(self.frame)
        pygame.display.set_caption(self.caption)
        sw, sh = self.frame.get_rect().size

        playerSize = (sw + sh) / 2 // 40
        player = Player(self.frame, playerSize, playerSize)

        self.manager.buttons.extend(self.buttonFrame.children)
        self.manager.setplayer(player)
        try:
            enemysize = 20  # 敌人大小，数值越大敌人越小
            screensize = (sw + sh) // 2
            # 创建敌人
            for i in range(self.enemy_num):
                one_enemy = Enemy(self.frame, screensize / enemysize, screensize / enemysize)
                self.manager.add(one_enemy)
                enemies.append(one_enemy)

            while self.running:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.close()
                            return
                        if event.key == pygame.K_TAB:
                            self.setting()
                    if event.type == pygame.QUIT:
                        self.close()
                        return
                if player.checkHurtOrDead(self.manager.sprites()):  # 受伤判定，同时检查玩家是否死亡
                    self.manager.updateCondition()
                    self.flush(player.rect.center)
                    self.close()
                    return

                # 摆放技能CD
                restPercent = max((player.lastSkillTime + player.skillSleepingTime - getTimeMil()) /
                                  player.skillSleepingTime, 0) if not Con.NoCD else 0  # CD剩余百分比
                cdRect = (-1, int(sh / 2), int(sw * restPercent), self.cdweight)
                pygame.draw.rect(self.frame, self.cdcolor, cdRect)

                # 摆放可冲刺时效果
                nowTime = getTimeMil()
                restPercent = (player.rushSleepTime + player.lastRushTime - nowTime) / player.rushSleepTime - Con.NoCD
                # restPercent为剩余百分比，NoCD成立则始终小于零
                r = 10
                if restPercent < 0:
                    r = random.randint(0, r + 5) if Con.ParticlesShowing else r + 5
                else:
                    r = (1 - restPercent) * r
                pygame.draw.circle(self.root, self.cdcolor, pygame.mouse.get_pos(), r)

                # 更新敌人和玩家状态
                process, iswinning = self.manager.updateCondition()
                if iswinning:
                    raise Exception("Winning!")

                # 计算信息
                livesmessage = ' '.join(["■"] * player.lives)
                message = f'Static:{getTimeSec() - self.manager.playerlastmovetime / 1000:.2f} Enemies:{self.enemy_num} Escapes:{countEscapeTimes()} Second:{getTimeSec():.1f} Process:{process / self.manager.endProcess:.2%}'

                # 摆放玩家血量
                textlives = self.Font.render(livesmessage, True, self.livescolor)
                w, h = textlives.get_rect().size
                self.frame.blit(textlives, (int(sw / 2 - w / 2), int(sh / 2 - h / 2)))

                # 摆放顶部文字
                text1 = self.Font.render(message, True, self.fontcolor)
                w, h = text1.get_rect().size
                sizeratio = w / sw
                text1after = pygame.transform.scale(text1, (int(sw), int(h / sizeratio)))
                aw = text1after.get_rect().width
                self.root.blit(text1after, (int(sw / 2 - aw / 2), 0))

                # 显示边框
                t = Con.ScreenBorderThick
                pygame.draw.rect(self.frame, self.boardColor, [0, 0, *self.size], t)

                # 刷新页面
                self.flush(player.rect.center)
                self.clock.tick(self.fps)
                addTime()
        finally:
            traceback.print_exc(file=sys.stderr)
            self.close()
            return getTimeSec(), countEscapeTimes(), process, player.olives, iswinning

    def flush(self, playerPos=None):  # 只有在RelShowing成立时，playerPos才会起作用
        pygame.display.update()
        self.root.fill(self.background)

        # 更新manager内的角色
        self.manager.flush()
        # 更新Frame
        if Con.RelShowing and playerPos:
            pos = [-i for i in playerPos]
            pos[0] += Con.SW // 2
            pos[1] += Con.SH // 2
            self.frame.print(pos)
        else:
            self.frame.print((0, 0))
        # 更新按钮Frame
        if Con.ButtonShowing:
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
