from setuptools import setup, find_packages

setup(
    name="Info_Server",
    version="0.0.1",
    packages=find_packages(),
    scripts=['src/info_server.py'],
    console=['src/info_server.py'],
    author="Rodrigo 'Gunisalvo' Leite",
    author_email="gunisalvo@gmail.com",
    description="Consul Guinea Pig",
    install_requires=[
        "flask"
    ],
    url="https://github.com/Entrementes/environments",
)