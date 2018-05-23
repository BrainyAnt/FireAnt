from setuptools import setup

setup(
    name='fireant',
    version='1.0.0a1',
    description='BrainyAnt library for linking brainyant.com to a robot.',
    url='https://github.com/BrainyAnt/FireAnt',
    author='Andrei Brumboiu',
    author_email='andrei.brumboiu@brainyant.com',
    license='Apache',
    packages=['fireant'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Customer Service',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['pyrebase'],
    python_requires='>=3',
    zip_safe = False
)