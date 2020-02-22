#!/usr/bin/env python3

import math
import numpy as np
from OpenGL.GL import *
from OpenGL.arrays import vbo

import ctypes
import os
import sys

import pyrr

from mgl2d.app import App

from screen import Screen
from texture import Texture, load_texture
from shaders import ShaderProgram, get_shader_program

import pywavefront

app = App()
main_screen = Screen(800, 600, 'Drawable')
main_screen.print_info()


class MeshDrawable:
    _default_shader = None

    def __init__(self, pos_x=0.0, pos_y=0.0, size_x=100, size_y=100, scale_x=1, scale_y=1):
        self._angle = 0.

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)

        # Vertices
        self._vbo = glGenBuffers(1)

        # Texture coordinates
        self._vbo_uvs = glGenBuffers(1)

        glBindVertexArray(0)

        if self._default_shader is None:
            self._setup_default_shader()
        self.shader = self._default_shader

        #self.meshes_path = os.path.join(os.path.dirname(__file__), 'data/uv_sphere.obj')
        #self.meshes_path = os.path.join(os.path.dirname(__file__), 'data/box/box-V3F.obj')
        #self.meshes_path = os.path.join(os.path.dirname(__file__), 'data/box/box-C3F_V3F.obj')
        #self.meshes_path = os.path.join(os.path.dirname(__file__), 'data/box/box-N3F_V3F.obj')
        self.meshes_path = os.path.join(os.path.dirname(__file__), 'data/box/box-T2F_V3F.obj')
        #self.meshes_path = os.path.join(os.path.dirname(__file__), 'data/box/box-T2F_C3F_V3F.obj')
        #self.meshes_path = os.path.join(os.path.dirname(__file__), 'data/box/box-T2F_N3F_V3F.obj')

        self.meshes = pywavefront.Wavefront(self.meshes_path)

    def __del__(self):
        glDeleteBuffers(1, self._vbo)
        self._vbo = None
        glDeleteBuffers(1, self._vbo_uvs)
        self._vbo_uvs = None
        glDeleteVertexArrays(1, self._vao)
        self._vao = None

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        #self._m_rotation = Matrix4.rotate_z(self._angle)
        #self._is_transform_invalid = True

    def _setup_default_shader(self):
        self._default_shader = get_shader_program('C3F_V3F')

    def draw(self, screen):
        texture = load_texture('data/texture.png')
        if texture is not None:
            texture.bind()

        rot_x = pyrr.Matrix44.from_x_rotation(0.0)
        rot_y = pyrr.Matrix44.from_y_rotation(0.0)
        transform_matrix = rot_x * rot_y

        projection_matrix = pyrr.Matrix44.identity()
        projection_matrix *= pyrr.Matrix44.from_scale(np.array([.5, .5, .5], dtype=np.float32))
        projection_matrix *= pyrr.Matrix44.from_x_rotation(self._angle)

        shader = get_shader_program('C3F_V3F')
        if shader is not None:
            shader.bind()
            shader.set_uniform_matrix4('model', transform_matrix)
            shader.set_uniform_matrix4('projection', projection_matrix)

        self.draw_meshes(self.meshes)

        if texture is not None:
            texture.unbind()

        if shader is not None:
            shader.unbind()

    def draw_meshes(self, instance, lighting_enabled=True, textures_enabled=True):
        # Draw Wavefront instance
        if isinstance(instance, pywavefront.Wavefront):
            self.draw_materials(instance.materials, lighting_enabled=lighting_enabled, textures_enabled=textures_enabled)
        # Draw single material
        elif isinstance(instance, pywavefront.Material):
            self.draw_material(instance, lighting_enabled=lighting_enabled, textures_enabled=textures_enabled)
        # Draw dict of materials
        elif isinstance(instance, dict):
            self.draw_materials(instance, lighting_enabled=lighting_enabled, textures_enabled=textures_enabled)
        else:
            raise ValueError("Cannot figure out how to draw: {}".format(instance))

    def draw_materials(self, materials, lighting_enabled=True, textures_enabled=True):
        for name, material in materials.items():
            self.draw_material(material, lighting_enabled=lighting_enabled, textures_enabled=textures_enabled)

    VERTEX_FORMATS = {
        'V3F': GL_V3F,
        'C3F_V3F': GL_C3F_V3F,
        'N3F_V3F': GL_N3F_V3F,
        'T2F_V3F': GL_T2F_V3F,
        # 'C3F_N3F_V3F': GL_C3F_N3F_V3F,  # Unsupported
        'T2F_C3F_V3F': GL_T2F_C3F_V3F,
        'T2F_N3F_V3F': GL_T2F_N3F_V3F,
        # 'T2F_C3F_N3F_V3F': GL_T2F_C3F_N3F_V3F,  # Unsupported
    }

    def draw_material(self, material, face=GL_FRONT_AND_BACK, lighting_enabled=True, textures_enabled=True):
        if material.gl_floats is None:
            material.gl_floats = (GLfloat * len(material.vertices))(*material.vertices)
            material.triangle_count = len(material.vertices) / material.vertex_size

        vertex_format = self.VERTEX_FORMATS.get(material.vertex_format)
        if not vertex_format:
            raise ValueError("Vertex format {} not supported".format(material.vertex_format))

        #print(f"{material.triangle_count}, {material.vertex_format} ({vertex_format}): {material.vertices}")

        if textures_enabled:
            # Fall back to ambient texture if no diffuse
            texture = material.texture or material.texture_ambient
            if texture and material.has_uvs:
                pass
                #bind_texture(texture)
            else:
                pass
                #glDisable(GL_TEXTURE_2D)

        if lighting_enabled and material.has_normals:
            pass
            #glMaterialfv(face, GL_DIFFUSE, gl_light(material.diffuse))
            #glMaterialfv(face, GL_AMBIENT, gl_light(material.ambient))
            #glMaterialfv(face, GL_SPECULAR, gl_light(material.specular))
            #glMaterialfv(face, GL_EMISSION, gl_light(material.emissive))
            #glMaterialf(face, GL_SHININESS, min(128.0, material.shininess))
            #glEnable(GL_LIGHT0)
            #glEnable(GL_LIGHTING)
        else:
            pass
            #glDisable(GL_LIGHTING)
            #glColor4f(*material.ambient)

        #glInterleavedArrays(vertex_format, 0, material.gl_floats)
        #glDrawArrays(GL_TRIANGLES, 0, int(material.triangle_count))



        #~ glBindVertexArray(self._vao)
        #~ bufdata = vbo.VBO(np.ascontiguousarray([
            #~ 0, 0,  0, 0, 0,
            #~ 0, 1,  0, 1, 0,
            #~ 1, 1,  1, 1, 0,
            #~ 1, 0,  1, 0, 1,
        #~ ], dtype=np.float32))
        #~ glEnableVertexAttribArray(0)
        #~ glEnableVertexAttribArray(1)
        #~ bufdata.bind()
        #~ glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))
        #~ glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        #~ glBindVertexArray(0)

        #~ glBindVertexArray(self._vao)
        #~ glDrawArrays(GL_TRIANGLE_FAN, 0, bufdata.size // 5)
        #~ bufdata.unbind()
        #~ glBindVertexArray(0)



        glBindVertexArray(self._vao)
        bufdata = vbo.VBO(np.ascontiguousarray(material.vertices, dtype=np.float32))
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        bufdata.bind()
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glBindVertexArray(0)

        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLES, 0, bufdata.size // 5)
        bufdata.unbind()
        glBindVertexArray(0)


mesh = MeshDrawable()

def draw_frame(screen):
    mesh.draw(screen)

def update_frame(delta_ms):
    mesh.angle += delta_ms / 1000
    pass

print(f"Textures: {load_texture.cache_info()}")
print(f"Shader Programs: {get_shader_program.cache_info()}")

app.run(main_screen, draw_frame, update_frame)
