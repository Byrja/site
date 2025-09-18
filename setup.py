from setuptools import setup, find_packages

setup(
    name="financial-telegram-bot",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==20.0",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "cryptography==41.0.0",
        "psutil==5.9.5",
        "portalocker==2.7.0"
    ],
    author="Financial Bot Developer",
    description="A Telegram bot for financial management with reminders",
    python_requires=">=3.7",
)