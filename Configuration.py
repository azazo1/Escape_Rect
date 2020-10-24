# coding=utf-8
from platform import system

Version = '0.45.7'
Font = r'consola.ttf'
Password = 'Azazo1Best'  # 角色无敌等功能需输入的密码
RelShowing = False  # 按照角色位置显示屏幕（角色始终在屏幕中间）
ButtonShowing = system() != 'Windows'  # 是否显示按钮(Linux显示)
EnemySleepTimeShowing = True  # 敌人是否显示间隙时间
ParticlesShowing = True  # 是否显示跳跃粒子
Invincible = False  # 无敌状态
ButtonSize = 50
ButtonMargin = 20
ScreenSize = SW, SH = (700, 400)
MinSize = 300, 200
LeastEnemy = 1
MostEnemy = 5
BackGround = (210, 105, 30)
ButtonColor = (70, 70, 70)
ButtonBorderColor = (50, 50, 50)
FontColor = (5, 5, 5)
FPS = 60
