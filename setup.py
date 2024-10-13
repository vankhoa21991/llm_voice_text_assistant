from setuptools import setup, find_packages

setup(
    name="VirAsst",  # Replace with your package name
    version="0.1.0",  # Initial version of your package
    description="A FastAPI app for AI assistant",  # Short description
    author="Van Khoa",  # Your name
    author_email="vankhoa21991@gmail.com",  # Your email
    packages=find_packages(),  # Automatically find all packages in your directory
    install_requires=[
        "fastapi",  # FastAPI dependency
        "uvicorn",  # Uvicorn for running the app
        # Add any other dependencies your project needs
        "pydantic",
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',  # Python version requirement
    entry_points={
        'console_scripts': [
            'start-fastapi=fastapi.app:main',  # Custom command to run the app
        ],
    },
)