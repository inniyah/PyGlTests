#!/usr/bin/env python3

import math
import numpy as np
from OpenGL.GL import *

import pyrr

from mgl2d.app import App
from mgl2d.graphics.shader_program import ShaderProgram
from mgl2d.graphics.screen import Screen
from mgl2d.graphics.texture import Texture
from mgl2d.math.matrix4 import Matrix4
from mgl2d.math.vector2 import Vector2

app = App()
main_screen = Screen(800, 600, 'Drawable')
main_screen.print_info()

class TestDrawable:
    _default_shader = None

    def __init__(self, pos_x=0.0, pos_y=0.0, size_x=100, size_y=100, scale_x=1, scale_y=1):
        self._texture = None
        self._shader = None

        self._angle = 0.

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)

        # Vertices
        self._vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        self._vertices = np.array([0, 0, 0, 1, 1, 1, 1, 0], dtype=np.int16)
        glBufferData(GL_ARRAY_BUFFER, self._vertices.nbytes, self._vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_UNSIGNED_SHORT, GL_FALSE, 0, None)

        # Texture coordinates
        self._vbo_uvs = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_uvs)
        self._texture_coordinates = np.array([0, 0, 0, 1, 1, 1, 1, 0], dtype=np.int16)
        glBufferData(GL_ARRAY_BUFFER, self._texture_coordinates.nbytes, self._texture_coordinates, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_UNSIGNED_SHORT, GL_FALSE, 0, None)

        glBindVertexArray(0)
        if self._default_shader is None:
            self._setup_default_shader()
        self.shader = self._default_shader

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, texture):
        self._texture = texture

    @property
    def shader(self):
        return self._shader

    @shader.setter
    def shader(self, shader):
        self._shader = shader

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        #self._m_rotation = Matrix4.rotate_z(self._angle)
        #self._is_transform_invalid = True

    def _setup_default_shader(self):
        vertex_shader = """
        #version 330 core

        uniform mat4 model;
        uniform mat4 projection;

        layout(location=0) in vec2 vertex;
        layout(location=1) in vec2 uv;

        out vec2 uv_out;

        void main() {
            vec4 vertex_world = model * vec4(vertex, 0, 1);
            gl_Position = projection * vertex_world;
            uv_out = uv;
        }
        """

        fragment_shader = """
        #version 330 core

        in vec2 uv_out;
        out vec4 color;

        uniform sampler2D tex;

        void main() {
            color = texture(tex, uv_out);
        }
        """

        self._default_shader = ShaderProgram.from_sources(vert_source=vertex_shader, frag_source=fragment_shader)

    def draw(self, screen):
        if self._texture is not None:
            self._texture.bind()

        rot_x = pyrr.Matrix44.from_x_rotation(0.0)
        rot_y = pyrr.Matrix44.from_y_rotation(0.0)
        transform_matrix = rot_x * rot_y

        projection_matrix = pyrr.Matrix44.identity()
        projection_matrix = pyrr.Matrix44.from_x_rotation(self._angle)

        if self._shader is not None:
            self._shader.bind()
            self._shader.set_uniform_matrix4('model', transform_matrix)
            self._shader.set_uniform_matrix4('projection', projection_matrix)

        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, len(self._vertices))
        glBindVertexArray(0)

        if self._texture is not None:
            self._texture.unbind()

        if self._shader is not None:
            self._shader.unbind()





cube = TestDrawable()
cube.texture = Texture.load_from_file('data/texture.png')

def draw_frame(screen):
    cube.draw(screen)

def update_frame(delta_ms):
    cube.angle += delta_ms / 1000
    pass

app.run(main_screen, draw_frame, update_frame)
