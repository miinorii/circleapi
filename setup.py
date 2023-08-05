from setuptools import setup

setup(
    name="circleapi",
    author="miinorii",
    version="2023.8.5",
    packages=["circleapi"],
    description="osu! apiv2 python wrapper",
    long_description="osu! apiv2 python wrapper",
    keywords=["osu!", "apiv2", "wrapper"],
    url="https://github.com/miinorii/circleapi",
    install_requires=[
        "httpx[http2]>=0.24.1",
        "pydantic>=2.1.1",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.10"
)
