from enum import Enum
from pathlib import Path
from functools import lru_cache

from OpenGL.GL import *


class ShaderType(Enum):
    VERTEX = GL_VERTEX_SHADER
    GEOMETRY = GL_GEOMETRY_SHADER
    FRAGMENT = GL_FRAGMENT_SHADER


class ShaderProgram(object):
    def __init__(self):
        self._uniforms = {}
        self._program_id = None

    def release(self):
        if self._program_id is None:
            return

        shaders_id = glGetAttachedShaders(self._program_id)
        for shader_id in shaders_id:
            glDetachShader(self._program_id, shader_id)
            glDeleteShader(shader_id)

        glDeleteProgram(self._program_id)

    @property
    def program_id(self):
        if self._program_id is None:
            self._program_id = glCreateProgram()
        return self._program_id

    def attach_shader(self, source_code, shader_type):
        # TODO: Check if shader_type is a ShaderType
        shader_id = glCreateShader(shader_type.value)
        glShaderSource(shader_id, source_code)
        glCompileShader(shader_id)
        glAttachShader(self.program_id, shader_id)

    def attach_shader_from_file(self, file_name, shader_type):
        source_code = Path(file_name).read_text()
        self.attach_shader(source_code=source_code, shader_type=shader_type)

    @staticmethod
    def from_files(vert_file=None, geom_file=None, frag_file=None):
        program = ShaderProgram()
        if vert_file is not None:
            program.attach_shader_from_file(file_name=vert_file, shader_type=ShaderType.VERTEX)
        if geom_file is not None:
            program.attach_shader_from_file(file_name=geom_file, shader_type=ShaderType.GEOMETRY)
        if frag_file is not None:
            program.attach_shader_from_file(file_name=frag_file, shader_type=ShaderType.FRAGMENT)

        program.link()
        log_txt = glGetProgramInfoLog(program._program_id)
        if log_txt: print(f"Shader program log: {log_txt}")
        return program

    @staticmethod
    def from_sources(vert_source=None, geom_source=None, frag_source=None):
        program = ShaderProgram()
        if vert_source is not None:
            program.attach_shader(source_code=vert_source, shader_type=ShaderType.VERTEX)
        if geom_source is not None:
            program.attach_shader(source_code=geom_source, shader_type=ShaderType.GEOMETRY)
        if frag_source is not None:
            program.attach_shader(source_code=frag_source, shader_type=ShaderType.FRAGMENT)

        program.link()
        log_txt = glGetProgramInfoLog(program._program_id)
        if log_txt: print(f"Shader program log: {log_txt}")
        return program

    def link(self):
        glLinkProgram(self._program_id)

    def bind(self):
        glUseProgram(self._program_id)

    def unbind(self):
        glUseProgram(0)

    def get_uniform(self, uniform_name):
        uniform = self._uniforms.get(uniform_name)
        if not uniform:
            uniform = glGetUniformLocation(self._program_id, uniform_name)
            self._uniforms[uniform_name] = uniform

        return uniform

    def set_uniform_matrix4(self, uniform_name, matrix):
        uniform = self.get_uniform(uniform_name)
        glUniformMatrix4fv(uniform, 1, GL_FALSE, matrix)

    def set_uniform_1i(self, uniform_name, value):
        uniform = self.get_uniform(uniform_name)
        glUniform1i(uniform, value)

    def set_uniform_1f(self, uniform_name, value):
        uniform = self.get_uniform(uniform_name)
        glUniform1f(uniform, value)

    def set_uniform_1fv(self, uniform_name, values):
        uniform = self.get_uniform(uniform_name)
        glUniform1fv(uniform, len(values), values)

    def set_uniform_2f(self, uniform_name, v1, v2):
        uniform = self.get_uniform(uniform_name)
        glUniform2f(uniform, v1, v2)

    def set_uniform_2fv(self, uniform_name, values):
        uniform = self.get_uniform(uniform_name)
        glUniform2fv(uniform, len(values), values)

    def set_uniform_3f(self, uniform_name, v1, v2, v3):
        uniform = self.get_uniform(uniform_name)
        glUniform3f(uniform, v1, v2, v3)

    def set_uniform_4f(self, uniform_name, v1, v2, v3, v4):
        uniform = self.get_uniform(uniform_name)
        glUniform4f(uniform, v1, v2, v3, v4)

def shader_program_V3F():
    vertex_shader = """
        #version 330 core

        uniform mat4 model;
        uniform mat4 projection;

        layout(location=0) in vec3 vertex;

        void main() {
            vec4 vertex_world = model * vec4(vertex, 1);
            gl_Position = projection * vertex_world;
        }
    """

    fragment_shader = """
        #version 330 core

        out vec4 color;

        void main() {
            color = vec4(0.5, 0.5, 0.5, 0.5);
        }
    """

    return ShaderProgram.from_sources(vert_source=vertex_shader, frag_source=fragment_shader)

def shader_program_C3F_V3F():
    vertex_shader = """
        #version 330 core

        uniform mat4 model;
        uniform mat4 projection;

        layout(location=0) in vec3 vertex;
        layout(location=1) in vec3 color_in;

        out vec3 color_out;

        void main() {
            vec4 vertex_world = model * vec4(vertex, 1);
            gl_Position = projection * vertex_world;
            color_out = color_in;
        }
    """

    fragment_shader = """
        #version 330 core

        in vec3 color_out;
        out vec4 color;

        void main() {
            color = vec4(color_out, 0.5);
        }
    """

    return ShaderProgram.from_sources(vert_source=vertex_shader, frag_source=fragment_shader)

def shader_program_T2F_V3F():
    vertex_shader = """
        #version 330 core

        uniform mat4 model;
        uniform mat4 projection;

        layout(location=0) in vec3 vertex;
        layout(location=1) in vec2 uv;

        out vec2 uv_out;

        void main() {
            vec4 vertex_world = model * vec4(vertex, 1);
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

    return ShaderProgram.from_sources(vert_source=vertex_shader, frag_source=fragment_shader)

SHADER_PROGRAMS = {
    'V3F':              shader_program_V3F,
    'C3F_V3F':          shader_program_C3F_V3F,
    #'N3F_V3F':          shader_program_N3F_V3F,
    'T2F_V3F':          shader_program_T2F_V3F,
    #'C3F_N3F_V3F':      shader_program_C3F_N3F_V3F,  # Unsupported
    #'T2F_C3F_V3F':      shader_program_T2F_C3F_V3F,
    #'T2F_N3F_V3F':      shader_program_T2F_N3F_V3F,
    #'T2F_C3F_N3F_V3F':  shader_program_T2F_C3F_N3F_V3F,  # Unsupported
}

@lru_cache(maxsize=None)  # Boundless cache
def get_shader_program(id):
    return SHADER_PROGRAMS[id]()
