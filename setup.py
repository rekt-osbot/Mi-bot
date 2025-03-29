from setuptools import setup, find_packages

setup(
    name="marketbot",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-telegram-bot>=13.0",
        "python-dotenv>=0.19.0",
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
    ],
    python_requires=">=3.8",
    description="Market Intelligence Bot for financial news and insights",
    author="Gammee Team",
) 