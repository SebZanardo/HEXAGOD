import asyncio  # For web builds of the game
from config.core import Core


def main():
    app = Core()
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
