'''Autonomous Agent Movement: Paths and Wandering

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

This code is essentially the same as the base for the previous steering lab
but with additional code to support this lab.

'''
from pyglet.window import key
from obstacle import Obstacle
from pyglet.window.key import O
from graphics import egi, KEY
from pyglet import window, clock
from pyglet.gl import *

from vector2d import Vector2D
from world import World
from agent import Agent, AGENT_MODES  # Agent with seek, arrive, flee and pursuit


def on_mouse_press(x, y, button, modifiers):
    if button == 1:  # left
        world.target = Vector2D(x, y)


def on_key_press(symbol, modifiers):
    if symbol == KEY.P:
        world.paused = not world.paused
    elif symbol in AGENT_MODES:
        for agent in world.agents:
            agent.mode = AGENT_MODES[symbol]
    elif symbol == KEY.A:
        world.agents.append(Agent(world,mode='separation'))
    ## LAB 09 STEP 1: Reset all paths to new random ones
    # ... 
    elif symbol == KEY.W:
        world.separation += 0.10
    elif symbol == KEY.S:
        world.separation -= 0.10
    elif symbol == KEY.E:
        world.cohesion += 0.10
    elif symbol == KEY.D:
        world.cohesion -= 0.10
    elif symbol == KEY.R:
        world.alignment += 0.10
    elif symbol == KEY.F:
        world.alignment -= 0.10
    elif symbol == KEY.I:
        for agent in world.agents:
            agent.show_info = not agent.show_info
    elif symbol == KEY.DOWN:
        for agent in world.agents:
            agent.wander_radius -= 2
    elif symbol == KEY.UP:
        for agent in world.agents:
            agent.wander_radius += 2
    


def on_resize(cx, cy):
    world.cx = cx
    world.cy = cy


if __name__ == '__main__':

    # create a pyglet window and set glOptions
    win = window.Window(width=1000, height=1000, vsync=True, resizable=True)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # needed so that egi knows where to draw
    egi.InitWithPyglet(win)
    # prep the fps display
    fps_display = window.FPSDisplay(win)
    # register key and mouse event handlers
    win.push_handlers(on_key_press)
    win.push_handlers(on_mouse_press)
    win.push_handlers(on_resize)
    

    # create a world for agents
    world = World(400, 400)
    # add one agent
    i = 0
    while i<20:
        world.agents.append(Agent(world,mode='group'))
        i+=1
    hunter = Agent(world,mode='wander',color='BLUE')
    world.hunter = hunter
    # unpause the world ready for movement
    world.paused = False

    while not win.has_exit:
        win.dispatch_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # show nice FPS bottom right (default)
        delta = clock.tick()
        world.update(delta)
        world.render()
        fps_display.draw()
        # swap the double buffer
        win.flip()

