from setuptools import setup

if __name__ == '__main__':
    setup(
        name='atpipeline',
        version='0.0.2',
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
