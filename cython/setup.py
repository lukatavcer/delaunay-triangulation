from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(['main.pyx', 'triangle.pyx'], compiler_directives={'language_level': "3"})
)