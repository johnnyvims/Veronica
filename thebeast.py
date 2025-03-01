import time
import sys
from colorama import Fore, Style, init

class SlowPrinter:
    """
    A class to handle slow printing of text with optional background and text colors.
    """
    def __init__(self):
        # Initialize colorama
        init(autoreset=True)
        
        # Define custom light red background color and white text
        self.LIGHT_RED = "\033[48;2;235;40;40m"  # Custom light red (RGB: 255, 102, 102)
        self.WHITE_TEXT = Fore.WHITE

    def slow_print(self, text, delay=0.1):
        """
        Prints the given text one character at a time with a delay.

        Args:
            text (str): The text to be printed.
            delay (float): Delay between each character (in seconds). Default is 0.1.
        """
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    def slow_print_with_bg(self, text, delay=0.3):
        """
        Prints the given text one character at a time with a background color and a delay.

        Args:
            text (str): The text to be printed.
            delay (float): Delay between each character (in seconds). Default is 0.1.
        """
        for char in text:
            sys.stdout.write(self.LIGHT_RED + self.WHITE_TEXT + char)
            sys.stdout.flush()
            time.sleep(delay)
        print()


