from setuptools import setup

setup(name='BoolNetController',
      version='0.0.1a',
      description='A Boolean Netowork-based controller for robotic agents',
      url='https://github.com/XanderC94/BoolNetController',
      author='XanderC94',
      author_email='alessandro.cevoli@outlook.com',
      license='GPL3',
      packages=['bncontroller'],
      install_requires=[
          'pandas',
          'numpy',
          'apted', 
          'networkx'
      ],
      zip_safe=False)