from setuptools import setup

setup(
    name="circleapi",
    author="miinorii",
    version="2023.11.26",
    packages=["circleapi"],
    description="Unoffical osu! apiv2 python wrapper",
    long_description="Unoffical osu! apiv2 python wrapper",
    keywords=["osu!", "apiv2", "wrapper"],
    url="https://github.com/miinorii/circleapi",
    install_requires=[
        "httpx[http2]>=0.24.1",
        "msgspec>=0.18.4",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.10"
)
