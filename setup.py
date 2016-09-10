from setuptools import setup, find_packages
setup(
    name = "Entrementes Environments",
    version = "0.1",
    packages = find_packages(),
    scripts = ['toolkit/environment_builder.py'],
    author = "Rodrigo 'Gunisalvo' Leite",
    author_email = "gunisalvo@gmail.com",
    description = "DevOps playground helper scripts.",
)