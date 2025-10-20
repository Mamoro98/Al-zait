"""Setup configuration for Al Zait News Agent."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="al-zait",
    version="1.0.0",
    author="Al Zait Development Team",
    author_email="info@alzait.news",
    description="Al Zait (الزيت): Autonomous Sudan News Agent powered by AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/al-zait",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "isort>=5.12.0",
            "mypy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "al-zait=main:main",
            "al-zait-test=run_once:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-username/al-zait/issues",
        "Source": "https://github.com/your-username/al-zait",
        "Documentation": "https://github.com/your-username/al-zait/blob/main/README.md",
    },
    keywords="news ai agent sudan arabic nlp automation telegram",
    include_package_data=True,
    package_data={
        "": ["config/*.template", "data/*.sql"],
    },
)
