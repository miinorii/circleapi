from setuptools import setup

setup(
    name="circleapi",
    author="miinorii",
    version="2023.7.15",
    packages=["circleapi"],
    install_requires=[
        "httpx[http2]>=0.24.1",
        "pydantic>=2.1.1",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.10"
)
