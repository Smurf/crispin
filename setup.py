from setuptools import setup
setup(
    name='crispin',
    version='0.1.0',
    author='Samuel Coles',
    author_email='me@smurf.codes',
    description='A utility to generate Kickstarts and ISOs for RHEL-alike Linux distros.',
    packages=['crispin'],
    entry_points = {
        'console_scripts': ['crispin = crispin.crispin:main']
    },
    install_requires = ['Jinja2>=3.1.3','MarkupSafe==2.1.3', 'python-dotenv>=1.0.1', 'pygvariant>=0.4.1']
)
