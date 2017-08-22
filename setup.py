'''
To create the wheel run - python setup.py bdist_wheel
'''

from setuptools import setup
import os

packages = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('lcopt'):
    # Ignore dirnames that start with '.'
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


my_package_files = []
my_package_files.extend(package_files(os.path.join('lcopt', 'assets')))
my_package_files.extend(package_files(os.path.join('lcopt', 'static')))
my_package_files.extend(package_files(os.path.join('lcopt', 'templates')))
my_package_files.extend(package_files(os.path.join('lcopt', 'bin')))
print(my_package_files)

setup(
    name='lcopt',
    version="0.4.2",
    packages=packages,
    author="P. James Joyce",
    author_email="pjamesjoyce@gmail.com",
    license=open('LICENSE.txt').read(),
    package_data={'lcopt': my_package_files},
    entry_points = {
        'console_scripts': [
            'lcopt-launcher = lcopt.bin.lcopt_launcher:main',
            'lcopt-bw2-setup = lcopt.bin.lcopt_bw2_setup:main',
            'lcopt-bw2-setup-forwast = lcopt.bin.lcopt_bw2_setup_forwast:main',
        ]
    },
    #install_requires=[
    #],
    include_package_data=True, 
    url="https://github.com/pjamesjoyce/lcopt/",
    download_url="https://github.com/pjamesjoyce/lcopt/archive/0.4.2.tar.gz",
    long_description=open('README.md').read(),
    description='An interactive tool for creating fully parameterised Life Cycle Assessment (LCA) foreground models',
    keywords=['LCA', 'Life Cycle Assessment', 'Foreground system', 'Background system', 'Foreground model', 'Fully parameterised'],
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)

# Also consider:
# http://code.activestate.com/recipes/577025-loggingwebmonitor-a-central-logging-server-and-mon/
