from setuptools import setup, find_packages

setup(
    name="financial-telegram-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==13.15",
        "requests==2.31.0"
    ],
    author="Financial Bot Developer",
    description="A Telegram bot for financial management",
    python_requires=">=3.7",
)