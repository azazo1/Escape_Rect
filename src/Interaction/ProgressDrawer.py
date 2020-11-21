# coding=utf-8
from src.Basic.Base import *
from bezier import Curve


class Loader:
    def __init__(self, screen: pygame.Surface, size: int = 50, pos=(0, 0), thick=None, twoPoint=False):
        """

        :param screen:
        :param size:
        :param pos:
        :param thick: 默认随着size变化而变化
        :param twoPoint: 弧线头尾都会动
        """
        self.__p = 0
        self.screen = screen
        self.size = (size, size)
        self.surfaceFrame = pygame.Surface(self.size)
        self.pos = pos
        self.font = getFont(Font, size // 5)
        self.thick = thick or size // 20
        self.twoPoint = twoPoint
        self.bezier_line = Curve(((.0, .15, .31, 1.0), (.0, .75, .86, 1.0)), 3)

    @property
    def percent(self):
        self.__p = self.__p % 1
        return self.__p

    @percent.setter
    def percent(self, p):
        self.__p = p % 1

    def generateAngle(self):
        if self.twoPoint:
            x, y = self.bezier_line.evaluate(float(self.__p))
            startAngle, endAngle = angleToFloat((-(y[0]) * 360) + 90), angleToFloat(-self.__p * 360 + 90)
            startAngle, endAngle = min(startAngle, endAngle), max(startAngle, endAngle)
            return startAngle, endAngle
        else:
            return angleToFloat((-self.__p) * 360 + 90), angleToFloat(90)

    def flush(self, screen=None):
        if screen:
            self.screen = screen
        self.surfaceFrame.fill(BackGround)
        start, end = self.generateAngle()
        pygame.draw.arc(self.surfaceFrame, ProgressBarColor, (*(0, 0), *self.size),
                        start, end, width=self.thick)
        text = self.font.render(f'{self.percent:.2%}', True, FontColor)
        printToCenter(self.surfaceFrame, text)
        if self.pos == CenterPosition:
            printToCenter(self.screen, self.surfaceFrame)
        else:
            self.screen.blit(self.surfaceFrame, self.pos)
