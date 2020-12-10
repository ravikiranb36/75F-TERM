import setuptools
with open('README.md','r') as fh:
       long_description = fh.read()
setuptools.setup(
       name = "rvzip",
       version = 1.0,
       author="Ravikirana B",
       author_email="ravikiranb36@gmail.com",
       description="It is ZIP and UNZIP tool",
       long_description=long_description,
       long_description_content_type="text/markdown",
       url="https://github.com/ravikiranb36/75F-TERM.io.git",
       packages=setuptools.find_packages(),
       classifiers=[
              "Programming Language :: Python :: 3",
              "License :: OSI Approved :: MIT License",
              "Operating System :: OS Independent",
       ],
       python_requires='>=3.7' ,
)