from setuptools import setup, find_packages

setup(
    name='multion',
    version='0.1.0',
    url='https://github.com/MULTI-ON/multion',
    author='Div Garg',
    author_email='div@multion.ai',
    description='MULTION API',
    packages=find_packages(),
    install_requires=['requests', 'flask', 'requests_oauthlib'],
)