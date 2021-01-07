# coding=utf-8
import random
import traceback
from src.Basic.Base import *
from src.Char.Enemy import Enemy
from src.Char.Player import Player
from src.GameControl import Controller

Con = Configuration


class GameResult:
    pass


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
        # self.buttonFrame = MyFrame(self.root, # TODO   新版本不再支持按钮
        #                            (self.size[0], Con.ButtonSize + 2 * Con.ButtonMargin),
        #                            (0,
        #                             self.root.get_rect().height - Con.ButtonSize - 2 * Con.ButtonMargin),
        #                            alpha=70)
        # [Button(self.buttonFrame, c) for c in range(4)]  # 创建按钮
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

    def gameloop(self, playerNum=1):
        """
        TODO 多人游戏
        TODO 返回GameResult
        """

        def countLives():
            totalLives = 0
            for player in self.manager.players:
                totalLives += player.lives
            return totalLives

        def countEscapeTimes():
            totalEscapeTimes = 0
            for enemy in self.manager.enemyHandler.getEnemies():
                totalEscapeTimes += enemy.movetimes
            return totalEscapeTimes

        pygame.init()
        process = 0
        situation = RUNNING
        self.running = True
        self.manager = Controller.GroupManager(self.frame)
        pygame.display.set_caption(self.caption)
        sw, sh = self.frame.get_size()

        playerSize = (sw + sh) / 2 // 40
        player_1 = Player(self.frame, playerSize, playerSize)

        # self.manager.buttons.extend(self.buttonFrame.children) TODO 新版本不再支持按钮
        self.manager.addPlayer(player_1)
        for i in range(playerNum - 1):
            self.manager.addPlayer(Player(self.frame, playerSize, playerSize))
        try:
            screensize = (sw + sh) // 2
            enemysize = 0.06  # 敌人大小
            # 创建敌人
            for i in range(self.enemy_num):
                one_enemy = Enemy(self.frame, screensize * enemysize, screensize * enemysize)
                self.manager.addEnemy(one_enemy)

            while self.running:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            situation = LOST
                            return
                        if event.key == pygame.K_TAB:
                            self.setting()
                    if event.type == pygame.QUIT:
                        return

                # 摆放技能CD
                if self.onePlayer:
                    restPercent = max((player_1.lastSkillTime + player_1.skillSleepingTime - getTimeMil()) /
                                      player_1.skillSleepingTime, 0) if not Con.NoCD else 0  # CD剩余百分比
                    cdRect = (-1, int(sh / 2), int(sw * restPercent), self.cdweight)
                    pygame.draw.rect(self.frame, self.cdcolor, cdRect)

                # 更新敌人和玩家状态
                process, situation = self.manager.updateSituation()
                if situation == WIN:
                    raise Exception("Winning!")
                if situation == LOST:
                    raise Exception("Lost...")

                # 计算信息
                livesmessage = ' '.join(["■"] * countLives())
                message = f'Enemies:{self.enemy_num} ' \
                          f'Escapes:{countEscapeTimes()} ' \
                          f'Second:{getTimeSec():.1f} ' \
                          f'Process:{process:.2%}'

                # 摆放玩家血量
                textlives = self.Font.render(livesmessage, True, self.livescolor)
                w, h = textlives.get_rect().size
                self.frame.blit(textlives, (int(sw / 2 - w / 2), int(sh / 2 - h / 2)))

                # 摆放顶部文字
                text1 = self.Font.render(message, True, self.fontcolor)
                w, h = text1.get_size()
                sizeratio = w / sw
                text1after = pygame.transform.scale(text1, (int(sw), int(h / sizeratio)))
                aw = text1after.get_rect().width
                self.root.blit(text1after, (int(sw / 2 - aw / 2), 0))

                # 显示边框
                pygame.draw.rect(self.frame, self.boardColor, [0, 0, *self.size], Con.ScreenBorderThick)

                # 刷新页面
                self.flush(player_1.pos)
                self.clock.tick(self.fps)
                addTime()
        finally:
            traceback.print_exc()
            self.close()
            return getTimeSec(), countEscapeTimes(), process, player_1.olives, situation

    def flush(self, playerPos=None):  # 只有在RelShowing成立时，playerPos才会起作用
        pygame.display.update()
        self.root.fill(self.background)

        # 更新manager内的角色
        self.manager.flush()
        # 更新Frame
        if Con.RelativeShowing and playerPos and self.onePlayer:
            pos = [-i for i in playerPos]
            pos[0] += Con.SW // 2
            pos[1] += Con.SH // 2
            self.frame.print(pos)
        else:
            self.frame.print((0, 0))
        # # 更新按钮Frame TODO 新版本不再支持按钮
        # if Con.ButtonShowing:
        #     self.buttonFrame.printChildren()
        #     self.buttonFrame.print()
        #
        # self.buttonFrame.fill(self.background)
        self.frame.fill(self.background)

    def close(self):
        self.running = False

    @property
    def onePlayer(self):
        return self.manager.playerHandler.length


def main():
    s = GameScreen((500, 200), fps=60)
    s.gameloop()
    pygame.quit()


if __name__ == '__main__':
    main()
