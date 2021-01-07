# coding=utf-8
from random import choice
from typing import List, Tuple, overload, Dict, Callable, Union
from src.Basic.Base import *
from src.Char.Character import MyChar
from src.Char.Player import Player
from src.Char.Enemy import Enemy


class MethodResult:
    def __init__(self, method: str, situation: bool):
        self.situation = situation
        self.method = method

    def __bool__(self):
        return self.situation

    def __eq__(self, other: str):
        return self.method == other

    def get_method(self):
        return self.method


class MethodsResult:
    def __init__(self, methods: Union[List[str], Tuple[str]], situation=True):
        self.methods = tuple((MethodResult(method, situation) for method in methods))  # type: Tuple[MethodResult]

    def have(self, method: str):
        return method in self.methods

    def get_methods(self):
        return self.methods


# class MouseMethod:
#     """
#     TODO 未来的版本不会再支持鼠标
#
#     将鼠标按键和事件绑定
#     """
#
#     def __init__(self, method: str, keys: List[int]):
#         self.method = method
#         self.keys = keys
#
#     def checkPress(self) -> MethodResult:
#         for i in self.keys:
#             try:
#                 if pygame.mouse.get_pressed(3)[i]:
#                     return MethodResult(self.method, True)
#             except Exception:
#                 pass
#         return MethodResult(self.method, False)


class KeyMethod:
    """
    将方法与键盘操作绑定的类
    """

    def __init__(self, method: str, keys: List[int]):
        self.method = method
        self.keys = keys

    def checkKey(self) -> MethodResult:
        for i in self.keys:
            try:
                if pygame.key.get_pressed()[i]:
                    return MethodResult(self.method, True)
            except Exception:
                pass
        return MethodResult(self.method, False)


class KeyMethodsManager:
    def __init__(self, methods_keys_Map: Dict[str, List[int]]):
        """
        :param methods_keys_Map: （方法->按键）对

        """
        self.map = methods_keys_Map

    def check(self, seq=0) -> MethodsResult:
        """
        检查被键盘触发的method
        :param seq: 所属对象在按键中的索引
        """
        get = []
        for method in self.map.keys():
            try:
                if KeyMethod(method, [self.map[method][seq]]).checkKey():  # 检查seq对应的键
                    get.append(method)
            except IndexError:
                pass
        return MethodsResult(get)


# class MouseMethodsManager:
#     """
#     TODO 未来的版本不会再支持鼠标
#     """
#
#     def __init__(self, methods_mouseKeys_Map: Dict[str, List[int]]):
#         self.map = methods_mouseKeys_Map
#
#     def check(self) -> MethodsResult:
#         get = []
#         for method in self.map.keys():
#             if MouseMethod(method, self.map[method]).checkPress():
#                 get.append(method)
#         return MethodsResult(get)


class GroupManager:
    """
    本类包含了 PlayerHandler 和 EnemyHandler
    """

    def __init__(self, targetScreen):
        super(GroupManager, self).__init__()
        self.lastIncreaseTime = getTimeMil()
        self.buttons = []
        # noinspection PyTypeChecker
        self.playerHandler = PlayerHandler(self)
        self.enemyHandler = EnemyHandler(self)
        self.process = 0  # 初始Process
        self.processIncrease = 0.05  # Process增长速度
        self.endProcess = 20  # 胜利Process
        self.target: MyFrame = targetScreen

    def addPlayer(self, player: Player):
        self.playerHandler.add(player)

    def addEnemy(self, enemy: Enemy):
        self.enemyHandler.add(enemy)

    @property
    def enemies(self):
        return self.enemyHandler.getEnemies()

    @property
    def players(self) -> List[Player]:
        return self.playerHandler.getPlayers()

    def updateSituation(self):
        """
        处理角色信息
        :return: 返回游戏进度(0~1) 和 当前情况
        """
        nowTime = getTimeMil()

        if nowTime - self.lastIncreaseTime > 1000:  # 增长process
            self.process += self.processIncrease
            self.lastIncreaseTime = nowTime

        # 处理角色信息
        self.playerHandler.handlePlayersActivities()
        self.enemyHandler.handleEnemiesActivities()

        if self.process > self.endProcess:  # 胜利判定
            condition = WIN
        elif self.playerHandler.checkAllDead():  # 检查玩家是否全部死亡
            condition = LOST
        else:
            condition = RUNNING
        return self.process / self.endProcess, condition

    def flush(self):
        """ TODO
        将角色信息刷新到屏幕上
        """
        self.enemyHandler.flush()
        self.playerHandler.flush()


class CharHandler:
    def __init__(self, belong: GroupManager):
        self.belong = belong
        self._elements: List[MyChar] = []

    def index(self, char: MyChar):
        return self._elements.index(char)

    def add(self, ele: MyChar):
        self._elements.append(ele)
        ele.belong = self
        ele.seq = self.length

    @property
    def length(self):
        return len(self._elements)

    @property
    def target(self) -> MyFrame:
        """返回目标窗口"""
        return self.belong.target

    def flush(self):
        for e in self._elements:
            if e:
                self.target.blit(e, e.start_pos)


class EnemyHandler(CharHandler):
    def __init__(self, belong: GroupManager):
        super(EnemyHandler, self).__init__(belong)
        self._enemies: List[Enemy] = []
        self._elements = self._enemies

    def add(self, enemy: Enemy):
        super(EnemyHandler, self).add(enemy)

    def getEnemies(self):
        return tuple(self._enemies)

    def getEnemy(self, seq: int):
        return self._enemies[seq]

    def handleEnemiesActivities(self):
        # TODO
        for seq in range(self.length):
            self._handleEnemyActivities(seq)

    def _handleEnemyActivities(self, seq: int):
        # 攻击静止玩家
        enemy = self.getEnemy(seq)
        staticPlayers = self.playerHandler.getStaticPlayers()
        if staticPlayers and not enemy.moving:
            enemy.summonPoint(player=choice(staticPlayers), hit=True)  # 追杀玩家
        enemy.update()

    @property
    def playerHandler(self):
        return self.belong.playerHandler


class PlayerHandler(CharHandler):
    def __init__(self, belong: GroupManager):
        super().__init__(belong)
        self._players: List[Player] = []
        self._elements = self._players
        self.methodManager = KeyMethodsManager(
            {  # TODO 将按键设置为引用Configuration
                PLAYER_LEFT: [pygame.K_a, pygame.K_LEFT],
                PLAYER_RIGHT: [pygame.K_d, pygame.K_RIGHT],
                PLAYER_SKILL: [pygame.K_s, pygame.K_DOWN],
                PLAYER_JUMP: [pygame.K_w, pygame.K_UP],
                # PLAYER_RUSH: [pygame.K_RSHIFT, pygame.K_LSHIFT],
            }
        )
        self.playerLastMoveTimeStamps = []  # 玩家上次移动时间
        self.playerMaxStaticTime = 5000  # 玩家最大静止时间
        self.playerLastPositions = []  # type:List[Tuple[int,int]]

    @property
    def enemyHandler(self):
        return self.belong.enemyHandler

    def add(self, player: Player):
        super(PlayerHandler, self).add(player)
        self.playerLastMoveTimeStamps.append(0)
        self.playerLastPositions.append(player.pos)

    def getPlayers(self) -> Tuple[Player]:
        return tuple(self._players)

    def getPlayer(self, seq: int) -> Player:
        """
        :param seq: 目标玩家在列表中的索引
        """
        return self._players[seq]

    def handlePlayersActivities(self):
        """处理所有玩家的动作"""
        for seq in range(self.length):
            self._handlePlayerActivities(seq)

    def _handlePlayerActivities(self, seq: int):
        """处理一个玩家的动作"""
        player = self.getPlayer(seq)
        # 检测受伤或死亡
        player.checkHurtOrDead(self.enemyHandler.getEnemies())
        if not player:
            return
        # 检测键盘
        awakened_key_methods = self.methodManager.check(seq)
        if awakened_key_methods.have(PLAYER_RIGHT):  # 向右走
            player.right()
        if awakened_key_methods.have(PLAYER_LEFT):  # 向左走
            player.left()
        if awakened_key_methods.have(PLAYER_SKILL):  # 技能判定
            player.skill()
        if awakened_key_methods.have(PLAYER_JUMP):  # 跳跃判定
            player.jump()
        # 检测玩家的移动
        self._detectMotion(seq)
        # 玩家掉落和跳跃的动作
        player.fall()
        player.update()

    def _getRelativeMousePos(self) -> Tuple[int, int]:
        tx, ty = self.target.start_pos  # type:int
        mx, my = pygame.mouse.get_pos()  # type:int
        return mx - tx, my - ty

    def _detectMotion(self, seq: int):
        """
        检测玩家是否移动
        :param seq: 目标玩家在管理器中的索引
        """
        nowTime = getTimeMil()
        player = self.getPlayer(seq)
        if self.playerLastPositions[seq] != player.pos:
            self.playerLastMoveTimeStamps[seq] = nowTime  # 重置静止时间
            self.playerLastPositions[seq] = player.pos
            return True  # 玩家移动了

    def checkStatic(self, seq) -> bool:
        """查询玩家是否进入静止状态(不动时间大于 playerMaxStaticTime )"""
        nowTime = getTimeMil()
        if nowTime > self.playerMaxStaticTime + self.playerLastMoveTimeStamps[seq]:
            return True

    def getStaticPlayers(self) -> List[Player]:
        """获得所有进入静止状态的玩家(不动时间大于 playerMaxStaticTime )"""
        get = []  # type:List[Player]
        for seq in range(self.length):
            if self.getPlayer(seq) and self.checkStatic(seq):
                get.append(self.getPlayer(seq))
        return get

    def checkAllDead(self) -> bool:
        return not any(self._players)
