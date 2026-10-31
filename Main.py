

#############################################
#   Andrew Chao - andrewchao7000@gmail.com  #
#   6/1/2026                                #
#############################################

import pygame_utils


pygame_width = 1920 #also change this to your screen resolution of whatever you are using to project
pygame_height = 1080

platform_update_frequency = 5 #updates 1once every X frames (0 is every frame) (lower numbers can mess with audio)
                             #(lower numbers also increase preformance)

pygame_utils.main_game_window(pygame_width,pygame_height, platform_update_frequency)


#CONTROLS:
# 'n' to show/hide platforms
# 'c' to recalibrate color #may not be working loll i tested before and it worked but nomw idk why but i gotta submit
# 'q' to quit