import sys
import os
from setuptools import setup

if sys.version_info < (3,4):
    sys.exit('Sorry, Python < 3.4 is not supported')

with open(os.path.join(os.path.dirname(__file__), "VERSION.txt")) as fp:
    version = fp.read().strip()

if __name__ == '__main__':
    setup(
        name='atpipeline',
        version=version,
        description='Scripts to run the Allen Institute array tomography pipeline',
        url='https://github.com/allenInstitute/atPipeline',
        packages=['atpipeline','atpipeline.pipelines','atpipeline.render_classes'],
        install_requires=[],
        zip_safe=False,
        entry_points = {
            'console_scripts': ['atcore=atpipeline.atcore:main',
                                'atbackend=atpipeline.atbackend:main'],
        }
    )
