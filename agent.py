'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''

from pyglet.window.key import Q, S
from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform
from path import Path

AGENT_MODES = {
    KEY._1: 'seek',
    KEY._2: 'arrive_slow',
    KEY._3: 'arrive_normal',
    KEY._4: 'arrive_fast',
    KEY._5: 'flee',
    KEY._6: 'pursuit',
    KEY._7: 'follow_path',
    KEY._8: 'wander',
}

class Agent(object):

    # NOTE: Class Object (not *instance*) variables!
    DECELERATION_SPEEDS = {
        'slow': 0.9,
        'normal': 0.6,
        'fast': 0.3
        ### ADD 'normal' and 'fast' speeds here
        # ...
        # ...
    }

    def __init__(self, world=None, scale=10.0, mass=1.0, mode='seek',color='ORANGE'):
        # keep a reference to the world object
        self.world = world
        self.mode = mode
        # where am i and where am i going? random start pos
        dir = radians(random()*360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  # easy scaling of agent size
        self.force = Vector2D()  # current steering force
        self.accel = Vector2D() # current acceleration due to force
        self.mass = mass
        # data for drawing this agent
        self.color = color
        self.vehicle_shape = [
            Point2D(-1.0,  0.6),
            Point2D( 1.0,  0.0),
            Point2D(-1.0, -0.6)
        ]
        ### path to follow?
        # self.path = ??
        ### wander details
        # self.wander_?? ...
        self.wander_dist = 2*scale
        self.wander_target = Vector2D(1,0)
        self.wander_radius = 0.5*scale
        self.wander_jitter = 10*scale
        self.bRadius = scale
        # limits?
        self.max_speed = 20.0 * scale
        self.max_force = 700
        self.hiding_spot = None
        self.tag_rad = scale*15
        ## max_force ??

        # debug draw info?
        self.show_info = False
        ## for group behaviours
        self.tagged = False
        self.cohesion_amt = self.world.cohesion
        self.alignment_amt = self.world.alignment
        self.separation_amt = self.world.separation

            


    def calculate(self,delta):
        # calculate the current steering force
        mode = self.mode
        if mode == 'group':
            self.tagNeighbors()
            force = Vector2D()
            force += self.wander(delta)
            force += self.separation()*self.separation_amt
            force += self.alignment()*self.alignment_amt
            force += self.cohesion()*self.cohesion_amt
            force += self.flee(self.world.hunter.pos)
        elif mode =='wander':
            force = self.wander(delta)
        else:
            force = Vector2D()
        self.force = force
        return force

    def update(self, delta):
        self.separation_amt = self.world.separation
        self.cohesion_amt = self.world.cohesion
        self.alignment_amt = self.world.alignment
        ''' update vehicle position and orientation '''
        # calculate and set self.force to be applied
        ## force = self.calculate()
        force = self.calculate(delta)  # <-- delta needed for wander
        force.truncate(self.max_force)
        ## limit force? <-- for wander
        # ...
        # determin the new accelteration
        self.accel = force / self.mass  # not needed if mass = 1.0
        # new velocity
        self.vel += self.accel * delta
        # check for limits of new velocity
        self.vel.truncate(self.max_speed)
        # update position
        self.pos += self.vel * delta
        # update heading is non-zero velocity (moving)
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)
    def tagNeighbors(self):
        for agent in self.world.agents:
            agent.tagged = False
            vt_to = self.pos - agent.pos
            gap = self.tag_rad + agent.bRadius
            if(vt_to.lengthSq()<gap**2):
                agent.tagged = True
    def separation(self):
        force = Vector2D()
        for agent in self.world.agents:
            if(self!=agent and agent.tagged):
                toSelf = self.pos - agent.pos
                force += toSelf.normalise()/float(toSelf.length())
        force.normalise()
        force *= self.max_speed
        return force - self.vel
        
    def alignment(self):
        heading = Vector2D()
        count = 0
        for agent in self.world.agents:
            if(self is not agent and agent.tagged):
                heading += agent.heading
        if count > 0:
            heading/=float(count)
            heading -= self.heading
        return (heading.normalise()*self.max_speed) 
    def cohesion(self):
        center_mass = Vector2D()
        force = Vector2D()
        count = 0
        for agent in self.world.agents:
            if(self is not agent and agent.tagged):
                center_mass += agent.pos
                count +=1
        if count>0:
            center_mass/=float(count)
            force = self.seek(center_mass)
        return force
    def render(self, color=None):
        ''' Draw the triangle agent with color'''
        # draw the path if it exists and the mode is follow
        # draw the ship
        egi.set_pen_color(name=self.color)
        if(self.tagged):
            egi.set_pen_color(name='RED')
        pts = self.world.transform_points(self.vehicle_shape, self.pos,
                                          self.heading, self.side, self.scale)
        # draw it!
        egi.closed_shape(pts)
        # draw wander info?
        
        wnd_pos = Vector2D(self.wander_dist,0)
        wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
        egi.green_pen()
        egi.circle(wld_pos, self.wander_radius)
        egi.red_pen()
        wnd_pos = self.wander_target + Vector2D(self.wander_dist,0)
        wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
        egi.circle(wld_pos,3)
        egi.set_pen_color(name='GREEN')
        # add some handy debug drawing info lines - force and velocity
        if self.show_info:
            s = 0.5 # <-- scaling factor
            # force
            egi.red_pen()
            egi.line_with_arrow(self.pos, self.pos + self.force * s, 5)
            # velocity
            egi.grey_pen()
            egi.line_with_arrow(self.pos, self.pos + self.vel * s, 5)
            # net (desired) change
            egi.white_pen()
            egi.line_with_arrow(self.pos+self.vel * s, self.pos+ (self.force+self.vel) * s, 5)
            egi.line_with_arrow(self.pos, self.pos+ (self.force+self.vel) * s, 5)

    def speed(self):
        return self.vel.length()

    #--------------------------------------------------------------------------
   

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

    def flee(self, hunter_pos):

        ''' move away from hunter position '''
        ## add panic distance (second)
        # ...
        ## add flee calculations (first)
        # ...
        dist = (hunter_pos - self.pos).length()
        if(dist<=self.tag_rad):
            desired_vel = (self.pos - hunter_pos).normalise()*self.max_speed
            return (desired_vel-self.vel)
        return Vector2D()
    def evade(self, pursuer):
        to_pursuer = pursuer.pos - self.pos
        lookAheadTime = to_pursuer.length()/(self.max_speed + pursuer.speed())
        return self.flee(pursuer.pos + pursuer.vel*lookAheadTime)
    def arrive(self, target_pos, speed):
        ''' this behaviour is similar to seek() but it attempts to arrive at
            the target position with a zero velocity'''
        decel_rate = self.DECELERATION_SPEEDS[speed]
        to_target = target_pos - self.pos
        dist = to_target.length()
        if dist > 0:
            # calculate the speed required to reach the target given the
            # desired deceleration rate
            speed = dist / decel_rate
            # make sure the velocity does not exceed the max
            speed = min(speed, self.max_speed)
            # from here proceed just like Seek except we don't need to
            # normalize the to_target vector because we have already gone to the
            # trouble of calculating its length for dist.
            desired_vel = to_target * (speed / dist)
            return (desired_vel - self.vel)
        return Vector2D(0, 0)


    def hide(self,hunter,objs):
        dist_to_hunter = (hunter.pos-self.pos).length()
        if(dist_to_hunter<self.world.hunter_threat_radius):
            if(dist_to_hunter<self.world.hunter_danger_radius):
                return self.flee(hunter.pos)
            dist_to_closest = float('inf')
            best_hiding_spot = None
            for obj in objs:
                hiding_spot = self.world.get_hide_pos(obj)
                hiding_dist = (hiding_spot-self.pos).lengthSq()
                if(hiding_dist<dist_to_closest):
                    dist_to_closest = hiding_dist
                    best_hiding_spot = hiding_spot
            if(best_hiding_spot):
                self.hiding_spot = best_hiding_spot
                return self.arrive(best_hiding_spot, 'fast')
        return self.evade(hunter)
    def wander(self, delta):
        ''' Random wandering using a projected jitter circle. '''
        wt = self.wander_target
        jitter_tts = self.wander_jitter*delta
        wt += Vector2D(uniform(-1,1)*jitter_tts,uniform(-1,1)*jitter_tts)
        wt.normalise()
        wt *= self.wander_radius
        target = wt + Vector2D(self.wander_dist, 0)
        wld_target = self.world.transform_point(target, self.pos, self.heading, self.side)
        return self.seek(wld_target)
        ## ...
