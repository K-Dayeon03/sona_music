from setuptools import find_packages, setup


setup(
    name="sona-backend",
    version="0.1.0",
    description="FastAPI backend for Sona AI music persona recommendations",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.30.0",
        "httpx>=0.27.0",
        "python-dotenv>=1.0.1",
    ],
)
