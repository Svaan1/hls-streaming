from colorama import Fore, Style, init

init(autoreset=True)


class ColorLogger:
    def __init__(self, name="App"):
        self.name = name

    def _log(self, level: str, color: str, message: str) -> None:
        print(f"{color}{level}{Style.RESET_ALL}:     {message}{Style.RESET_ALL}")

    def info(self, message: str) -> None:
        self._log("INFO", Fore.GREEN, message)

    def warning(self, message: str) -> None:
        self._log("WARNING", Fore.YELLOW, message)

    def error(self, message: str) -> None:
        self._log("ERROR", Fore.RED, message)

    def debug(self, message: str) -> None:
        self._log("DEBUG", Fore.BLUE, message)


logger = ColorLogger()
