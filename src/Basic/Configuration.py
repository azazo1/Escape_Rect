# coding=utf-8

Version = '0.45.8'
Font = r'consola.ttf'
Password = 'Azazo1Best'  # 启用高级功能需输入的密码
advanceFeatures = ['NoCD', 'Invincible']  # 高级功能，用来判断是否需要输入密码
FullScreen = False  # 是否全屏
RelShowing = False  # 按照角色位置显示屏幕（角色始终在屏幕中间）
ButtonShowing = True  # 是否显示按钮(Linux显示)
EnemySleepTimeShowing = True  # 敌人是否显示间隙时间
ParticlesShowing = True  # 是否显示跳跃粒子
Invincible = False  # 无敌状态
NoCD = False  # 没有技能CD
ButtonSize = 50  # 按钮直径
ButtonMargin = 20  # 按钮外边距
ScreenSizeRatio = 16 / 9  # 窗口宽高比
ScreenSize = SW, SH = (640, 360)  # 屏幕初始尺寸
MinSize = 400, 225  # 屏幕最小尺寸
ScreenBorderThick = 3  # 屏幕边框粗细
Lives = 5  # 玩家血量
LeastEnemy = 1  # 最小敌人数
MostEnemy = 5  # 最大敌人数
BackGround = (210, 105, 30)  # 背景颜色
ButtonColor = (70, 70, 70)  # 按钮颜色
ButtonBorderColor = (50, 50, 50)  # 按钮边框颜色
FontColor = (5, 5, 5)  # 字体颜色
ProgressBarColor = (255, 0, 0)  # 加载条颜色
FontRelation = 640 / 20  # 屏幕宽与字体大小比值
FPS = 60  # 帧率其他帧率可能会有问题
CenterPosition = 'center'  # 用来指示将元素打印在中间


def getAttr(name):
    return eval(name)
