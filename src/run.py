from src.core.system_analyst import SystemAnalyst

from logging import basicConfig, INFO


def main():
    basicConfig(level=INFO, force=True, filename="data/current.logs", filemode="w", encoding="utf-8")
    system_analyst = SystemAnalyst()
    system_analyst.run()


if __name__ == "__main__":
    main()
