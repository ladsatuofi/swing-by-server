from setuptools import setup

setup(
    name='sbserver',
    version='0.1.0',
    description='Swing By Server',
    url='https://github.com/ladsatuofi/swing-by-server',
    author='Matthew Scholefield',
    author_email='matthew331199@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='server',
    packages=['sbserver'],
    install_requires=[
        'Flask',
        'Flask-RESTPlus',
        'Flask-Redis',
        'gunicorn',
        'Werkzeug',
        'prettyparse'
    ],
    entry_points={
        'console_scripts': [
            'sbserver=sbserver.main:main',
        ],
    }
)
