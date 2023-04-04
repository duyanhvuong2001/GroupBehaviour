'''A 2d world that supports agents with steering behaviour

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''

from vector2d import Vector2D
from matrix33 import Matrix33
from graphics import egi


class World(object):

    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.target = Vector2D(cx / 2, cy / 2)
        self.hunter = None
        self.agents = []
        self.obstacles = []
        self.paused = True
        self.show_info = True
        self.cohesion = 1.0
        self.alignment = 1.0
        self.separation = 1.0
    def update(self, delta):
        if not self.paused:
            for agent in self.agents:
                agent.update(delta)
            self.hunter.update(delta)
            


    def render(self):
        for obstacle in self.obstacles:
            obstacle.render()
            hide_pos = self.get_hide_pos(obstacle)
            egi.white_pen()
            #draw line from hunter
            egi.line_by_pos(self.hunter.pos,hide_pos)
            egi.red_pen()
        egi.text_at_pos(0,20,"Separation Ratio(W/S): " + str("%.2f" % self.separation))
        egi.text_at_pos(0,40,"Cohesion Ratio(E/D): " + str("%.2f" %self.cohesion))
        egi.text_at_pos(0,60,"Alignment Ratio(R/F): " + str("%.2f" %self.alignment))
        for agent in self.agents:
            agent.render()
        egi.set_pen_color(name='YELLOW')
        if self.target:
            egi.cross(self.target,3)
        if self.hunter:
            self.hunter.render()
            # egi.circle(self.hunter.pos, self.agent_flee_radius)
            # egi.orange_pen()
            # egi.circle(self.hunter.pos,self.hunter_threat_radius)
            # egi.red_pen()
            # egi.circle(self.hunter.pos, self.hunter_danger_radius)
        egi.aqua_pen()
        last_a = self.agents[len(self.agents)-1]
        egi.circle(last_a.pos,last_a.tag_rad)
    def get_hide_pos(self, obstacle):
        dist_from_boundary = 50
        dist_away = obstacle.radius + dist_from_boundary
        hunter_to_obs = (obstacle.pos - self.hunter.pos).normalise()
        return (hunter_to_obs*dist_away)+obstacle.pos
    def wrap_around(self, pos):
        ''' Treat world as a toroidal space. Updates parameter object pos '''
        max_x, max_y = self.cx, self.cy
        if pos.x > max_x:
            pos.x = pos.x - max_x
        elif pos.x < 0:
            pos.x = max_x - pos.x
        if pos.y > max_y:
            pos.y = pos.y - max_y
        elif pos.y < 0:
            pos.y = max_y - pos.y

    def transform_points(self, points, pos, forward, side, scale):
        ''' Transform the given list of points, using the provided position,
            direction and scale, to object world space. '''
        # make a copy of original points (so we don't trash them)
        wld_pts = [pt.copy() for pt in points]
        # create a transformation matrix to perform the operations
        mat = Matrix33()
        # scale,
        mat.scale_update(scale.x, scale.y)
        # rotate
        mat.rotate_by_vectors_update(forward, side)
        # and translate
        mat.translate_update(pos.x, pos.y)
        # now transform all the points (vertices)
        mat.transform_vector2d_list(wld_pts)
        # done
        return wld_pts
    def transform_point(self, point, pos, forward, side):
        wld_pt = point.copy()
        mat = Matrix33()
        mat.rotate_by_vectors_update(forward,side)
        mat.translate_update(pos.x,pos.y)
        mat.transform_vector2d(wld_pt)
        return wld_pt