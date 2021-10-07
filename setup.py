from distutils.core import setup
from Cython.Build import cythonize

setup(
      name = 'Bedlam',
      ext_modules = cythonize("cubex.pyx")
)
