import sys
from setuptools import setup

if sys.version_info < (3,4):
    sys.exit('Sorry, Python < 3.4 is not supported')

if __name__ == '__main__':
    setup(
        name='atpipeline',
        version='0.0.3',
        description='Scripts to run the Allen Institute array tomography pipeline',
        url='https://github.com/allenInstitute/atPipeline',
        packages=['atpipeline'],
        install_requires=[],
        zip_safe=False,
        entry_points = {
            'console_scripts': ['atcore=atpipeline.atcore:main',
                                'atbackend=atpipeline.atbackend:main'],
        }
    )
