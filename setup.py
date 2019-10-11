from setuptools import setup

setup(name='BoolNetController',
      version='1.0.0',
      description='A Boolean Netowork-based controller for robotic agents',
      url='https://github.com/XanderC94/BoolNetController',
      author='XanderC94',
      author_email='alessandro.cevoli@outlook.com',
      license='GPL3',
      packages=['bncontroller'],
      install_requires=[
          'numpy',
          'pandas',
          'apted', 
          'networkx',
        #   'multiset',
          'singleton-decorator',
          'rpy2',
        #   'bunch'
        #   'Truths'
      ],
      zip_safe=False)
