import logging

import math
import numpy
import sdl2
from OpenGL.GL import *
from sdl2 import video
from pyrr import Matrix44

logger = logging.getLogger(__name__)


class Screen(object):
    def __init__(self, width, height, title='Window', alpha_blending=True, full_screen=False, gl_major=4, gl_minor=1):
        self._width = width
        self._height = height
        self._aspect_ratio = float(width) / float(height)
        self._viewport = sdl2.SDL_Rect(0, 0, width, height)
        self._full_screen = full_screen

        # Create the window
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            print(sdl2.SDL_GetError())

        self._window = sdl2.SDL_CreateWindow(str.encode(title),
                                             sdl2.SDL_WINDOWPOS_UNDEFINED,
                                             sdl2.SDL_WINDOWPOS_UNDEFINED, width, height,
                                             sdl2.SDL_WINDOW_OPENGL)

        if not self._window:
            print(sdl2.SDL_GetError())
            return

        # Set up OpenGL
        video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_MAJOR_VERSION, gl_major)
        video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_MINOR_VERSION, gl_minor)
        video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_PROFILE_MASK, video.SDL_GL_CONTEXT_PROFILE_CORE)
        self._context = sdl2.SDL_GL_CreateContext(self._window)

        self._x_angle = math.pi / 4
        self._y_angle = math.pi / 4
        self._projection_matrix_needs_refresh = True

        if alpha_blending:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if full_screen:
            self.full_screen = True

        # Post processing steps
        self._pp_steps = []

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def viewport(self):
        return self._viewport

    @property
    def is_opened(self):
        return self._window is not None

    @property
    def projection_matrix(self):
        if self._projection_matrix_needs_refresh:
            projection_matrix = Matrix44.identity()
            projection_matrix *= Matrix44.from_scale(numpy.array([.25, .25, .0001], dtype=numpy.float32))
            projection_matrix *= Matrix44.from_x_rotation(self._x_angle)
            projection_matrix *= Matrix44.from_y_rotation(self._y_angle)
            self._projection_matrix = projection_matrix
            self._projection_matrix = projection_matrix
            self._projection_matrix_needs_refresh = False
        return self._projection_matrix

    @property
    def full_screen(self):
        return self._full_screen

    @full_screen.setter
    def full_screen(self, value):
        sdl2.SDL_SetWindowFullscreen(self._window, value)

    @property
    def x_angle(self):
        return self._x_angle

    @property
    def y_angle(self):
        return self._y_angle

    @x_angle.setter
    def x_angle(self, value):
        self._x_angle = value
        self._projection_matrix_needs_refresh = True

    @y_angle.setter
    def y_angle(self, value):
        self._y_angle = value
        self._projection_matrix_needs_refresh = True

    def close(self):
        sdl2.SDL_GL_DeleteContext(self._context)
        self._context = None
        sdl2.SDL_DestroyWindow(self._window)
        self._window = None

    def begin_update(self):
        if len(self._pp_steps) > 0:
            self._pp_steps[0].fbo.bind()

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def end_update(self):
        if len(self._pp_steps) > 0:
            if len(self._pp_steps) > 1:
                for x in range(1, len(self._pp_steps)):
                    self._pp_steps[x].fbo.bind()
                    self._pp_steps[x - 1].draw(self)

            self._pp_steps[-1].fbo.unbind()
            self._pp_steps[-1].draw(self)

        sdl2.SDL_GL_SwapWindow(self._window)

    def add_postprocessing_step(self, step):
        self._pp_steps.append(step)

    def print_info(self):
        logger.info('Resolution: %dx%d ratio: %.2f' % (self._width, self._height, self._aspect_ratio))
        logger.info('Rendeer: %s (%s)' % (glGetString(GL_RENDERER), glGetString(GL_VENDOR)))
        logger.info('OpenGL: %s GLSL: %s' % (glGetString(GL_VERSION), glGetString(GL_SHADING_LANGUAGE_VERSION)))
