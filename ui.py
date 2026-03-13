import os
import sys
from typing import Optional


# ANSI color codes for terminal output
class Colors:
    """Color constants for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_GRAY = "\033[100m"

    # Theme colors
    THEME_LOGIN = BRIGHT_CYAN
    THEME_ADMIN = BRIGHT_GREEN
    THEME_ADMIN_ACCENT = YELLOW
    THEME_VOTER = BRIGHT_BLUE
    THEME_VOTER_ACCENT = MAGENTA


def colored(text: str, color: str) -> str:
    """Apply color to text."""
    return f"{color}{text}{Colors.RESET}"


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause(message: str = "Press Enter to continue...") -> None:
    """Pause execution and wait for user input."""
    input(f"\n  {Colors.DIM}{message}{Colors.RESET}")


def header(title: str, theme_color: str) -> None:
    """Display a formatted header."""
    width = 58
    top = f"  {theme_color}{'═' * width}{Colors.RESET}"
    mid = f"  {theme_color}{Colors.BOLD} {title.center(width - 2)} {Colors.RESET}{theme_color} {Colors.RESET}"
    bot = f"  {theme_color}{'═' * width}{Colors.RESET}"
    print(top)
    print(mid)
    print(bot)


def subheader(title: str, theme_color: str) -> None:
    """Display a formatted subheader."""
    print(f"\n  {theme_color}{Colors.BOLD}▸ {title}{Colors.RESET}")


def table_header(format_str: str, theme_color: str) -> None:
    """Display a table header."""
    print(f"  {theme_color}{Colors.BOLD}{format_str}{Colors.RESET}")


def table_divider(width: int, theme_color: str) -> None:
    """Display a table divider."""
    print(f"  {theme_color}{'─' * width}{Colors.RESET}")


def error(message: str) -> None:
    """Display an error message."""
    print(f"  {Colors.RED}{Colors.BOLD} {message}{Colors.RESET}")


def success(message: str) -> None:
    """Display a success message."""
    print(f"  {Colors.GREEN}{Colors.BOLD} {message}{Colors.RESET}")


def warning(message: str) -> None:
    """Display a warning message."""
    print(f"  {Colors.YELLOW}{Colors.BOLD} {message}{Colors.RESET}")


def info(message: str) -> None:
    """Display an info message."""
    print(f"  {Colors.GRAY}{message}{Colors.RESET}")


def menu_item(number: int, text: str, color: str) -> None:
    """Display a menu item."""
    print(f"  {color}{Colors.BOLD}{number:>3}.{Colors.RESET}  {text}")


def status_badge(text: str, is_good: bool) -> str:
    """Create a colored status badge."""
    if is_good:
        return f"{Colors.GREEN}{text}{Colors.RESET}"
    return f"{Colors.RED}{text}{Colors.RESET}"


def prompt(text: str) -> str:
    """Get user input with formatted prompt."""
    return input(f"  {Colors.BRIGHT_WHITE}{text}{Colors.RESET}").strip()


def masked_input(prompt_text: str = "Password: ") -> str:
    """Get masked password input."""
    print(f"  {Colors.BRIGHT_WHITE}{prompt_text}{Colors.RESET}", end="", flush=True)
    password = ""

    if sys.platform == "win32":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch == "\r" or ch == "\n":
                print()
                break
            elif ch == "\x08" or ch == "\b":
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                password += ch
                sys.stdout.write(f"{Colors.YELLOW}*{Colors.RESET}")
                sys.stdout.flush()
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch == "\r" or ch == "\n":
                    print()
                    break
                elif ch == "\x7f" or ch == "\x08":
                    if len(password) > 0:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += ch
                    sys.stdout.write(f"{Colors.YELLOW}*{Colors.RESET}")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return password


class UI:
    """User Interface class for managing display operations."""

    @staticmethod
    def display_welcome() -> None:
        """Display welcome message."""
        clear_screen()
        header("E-VOTING SYSTEM", Colors.THEME_LOGIN)
        print()

    @staticmethod
    def display_login_menu() -> str:
        """Display login menu and return choice."""
        menu_item(1, "Login as Admin", Colors.THEME_LOGIN)
        menu_item(2, "Login as Voter", Colors.THEME_LOGIN)
        menu_item(3, "Register as Voter", Colors.THEME_LOGIN)
        menu_item(4, "Exit", Colors.THEME_LOGIN)
        print()
        return prompt("Enter choice: ")

    @staticmethod
    def display_admin_dashboard(user_name: str, user_role: str) -> str:
        """Display admin dashboard and return choice."""
        clear_screen()
        header("ADMIN DASHBOARD", Colors.THEME_ADMIN)
        print(f"  {Colors.THEME_ADMIN}  ● {Colors.RESET}{Colors.BOLD}{user_name}{Colors.RESET}  {Colors.DIM}│  Role: {user_role}{Colors.RESET}")

        subheader("Candidate Management", Colors.THEME_ADMIN_ACCENT)
        menu_item(1, "Create Candidate", Colors.THEME_ADMIN)
        menu_item(2, "View All Candidates", Colors.THEME_ADMIN)
        menu_item(3, "Update Candidate", Colors.THEME_ADMIN)
        menu_item(4, "Delete Candidate", Colors.THEME_ADMIN)
        menu_item(5, "Search Candidates", Colors.THEME_ADMIN)

        subheader("Voting Station Management", Colors.THEME_ADMIN_ACCENT)
        menu_item(6, "Create Voting Station", Colors.THEME_ADMIN)
        menu_item(7, "View All Stations", Colors.THEME_ADMIN)
        menu_item(8, "Update Station", Colors.THEME_ADMIN)
        menu_item(9, "Delete Station", Colors.THEME_ADMIN)

        subheader("Polls & Positions", Colors.THEME_ADMIN_ACCENT)
        menu_item(10, "Create Position", Colors.THEME_ADMIN)
        menu_item(11, "View Positions", Colors.THEME_ADMIN)
        menu_item(12, "Update Position", Colors.THEME_ADMIN)
        menu_item(13, "Delete Position", Colors.THEME_ADMIN)
        menu_item(14, "Create Poll", Colors.THEME_ADMIN)
        menu_item(15, "View All Polls", Colors.THEME_ADMIN)
        menu_item(16, "Update Poll", Colors.THEME_ADMIN)
        menu_item(17, "Delete Poll", Colors.THEME_ADMIN)
        menu_item(18, "Open/Close Poll", Colors.THEME_ADMIN)
        menu_item(19, "Assign Candidates to Poll", Colors.THEME_ADMIN)

        subheader("Voter Management", Colors.THEME_ADMIN_ACCENT)
        menu_item(20, "View All Voters", Colors.THEME_ADMIN)
        menu_item(21, "Verify Voter", Colors.THEME_ADMIN)
        menu_item(22, "Deactivate Voter", Colors.THEME_ADMIN)
        menu_item(23, "Search Voters", Colors.THEME_ADMIN)

        subheader("Admin Management", Colors.THEME_ADMIN_ACCENT)
        menu_item(24, "Create Admin Account", Colors.THEME_ADMIN)
        menu_item(25, "View Admins", Colors.THEME_ADMIN)
        menu_item(26, "Deactivate Admin", Colors.THEME_ADMIN)

        subheader("Results & Reports", Colors.THEME_ADMIN_ACCENT)
        menu_item(27, "View Poll Results", Colors.THEME_ADMIN)
        menu_item(28, "View Detailed Statistics", Colors.THEME_ADMIN)
        menu_item(29, "View Audit Log", Colors.THEME_ADMIN)
        menu_item(30, "Station-wise Results", Colors.THEME_ADMIN)

        subheader("System", Colors.THEME_ADMIN_ACCENT)
        menu_item(31, "Save Data", Colors.THEME_ADMIN)
        menu_item(32, "Logout", Colors.THEME_ADMIN)
        print()
        return prompt("Enter choice: ")

    @staticmethod
    def display_voter_dashboard(user_name: str) -> str:
        """Display voter dashboard and return choice."""
        clear_screen()
        header("VOTER DASHBOARD", Colors.THEME_VOTER)
        print(f"  {Colors.THEME_VOTER}  ● {Colors.RESET}{Colors.BOLD}{user_name}{Colors.RESET}")

        subheader("Voting", Colors.THEME_VOTER_ACCENT)
        menu_item(1, "View Available Polls", Colors.THEME_VOTER)
        menu_item(2, "Cast Vote", Colors.THEME_VOTER)
        menu_item(3, "View Voting History", Colors.THEME_VOTER)

        subheader("Account", Colors.THEME_VOTER_ACCENT)
        menu_item(4, "View Profile", Colors.THEME_VOTER)
        menu_item(5, "Update Profile", Colors.THEME_VOTER)
        menu_item(6, "Change Password", Colors.THEME_VOTER)

        subheader("System", Colors.THEME_VOTER_ACCENT)
        menu_item(7, "Logout", Colors.THEME_VOTER)
        print()
        return prompt("Enter choice: ")