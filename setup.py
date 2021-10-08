from setuptools import setup
from Cython.Build import cythonize

setup(
      name = "Bedlam",
      version = "1.0.0",
      install_requires = ["numpy", "Cython"],
      ext_modules = cythonize("cube/cubex.pyx"),
      packages = ["cube"],
      entry_points = {
        "console_scripts": ["run = cube:run", "runx = cube.cubex:run"] }
)
