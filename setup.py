from setuptools import setup

setup(
    name="circleapi",
    author="miinorii",
    version="2023.6.24.2",
    packages=["circleapi"],
    install_requires=[
        "httpx[http2]>=0.24.1",
        "pydantic>=2.0",
        "python-dotenv>=1.0.0"
    ]
)
