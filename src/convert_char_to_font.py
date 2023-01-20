# -*- coding: utf-8 -*-

# 获取3500个汉字
with open("../dataset/chinese_3500.txt", "r", encoding="utf-8") as f:
    chars = list(f.read().strip())
    chars = chars[1:]

import pygame
# 初始化 pygame
pygame.init()

for char in chars:
    # 创建字体对象
    font = pygame.font.Font("../fonts/simkai.ttf", 100)
    # 渲染文本
    text = font.render(char, True, (0, 0, 0), (255, 255, 255))
    # 保存图像
    pygame.image.save(text, "../fonts/{}.png".format(char))
    print("save {} png done!".format(char))