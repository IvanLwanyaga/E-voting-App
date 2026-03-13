import datetime
import hashlib
import random
import string
from typing import Dict, List, Optional, Any
from models import (
    Admin, Voter, Candidate, VotingStation, Position, Poll, AuditLog
)
from ui import clear_screen, pause, prompt, masked_input, error, success, warning, info, subheader, header


class AuthService:
    """Service class for authentication operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def login_admin(admins: Dict[int, Dict], username: str, password: str) -> Optional[Admin]:
        """Authenticate admin login."""
        hashed = AuthService.hash_password(password)
        for admin_data in admins.values():
            if (admin_data["username"] == username and
                admin_data["password"] == hashed and
                admin_data["is_active"]):
                return Admin(
                    admin_data["id"], admin_data["username"], admin_data["full_name"],
                    admin_data["email"], admin_data["password"], admin_data["role"],
                    admin_data["is_active"]
                )
        return None

    @staticmethod
    def login_voter(voters: Dict[int, Dict], voter_card: str, password: str) -> Optional[Voter]:
        """Authenticate voter login."""
        hashed = AuthService.hash_password(password)
        for voter_data in voters.values():
            if (voter_data["voter_card_number"] == voter_card and
                voter_data["password"] == hashed and
                voter_data["is_active"] and
                voter_data["is_verified"]):
                return Voter(
                    voter_data["id"], voter_data["full_name"], voter_data["national_id"],
                    voter_data["date_of_birth"], voter_data["gender"], voter_data["address"],
                    voter_data["phone"], voter_data["email"], voter_data["password"],
                    voter_data["voter_card_number"], voter_data["station_id"],
                    voter_data["is_verified"], voter_data["is_active"]
                )
        return None

    @staticmethod
    def register_voter(voters: Dict[int, int], voter_id_counter: int, stations: Dict[int, Dict]) -> Optional[Voter]:
        """Register a new voter."""
        clear_screen()
        header("VOTER REGISTRATION", "\033[94m")  # THEME_VOTER
        print()

        full_name = prompt("Full Name: ")
        if not full_name:
            error("Name cannot be empty.")
            pause()
            return None

        national_id = prompt("National ID Number: ")
        if not national_id:
            error("National ID cannot be empty.")
            pause()
            return None

        # Check for duplicate national ID
        for voter in voters.values():
            if voter["national_id"] == national_id:
                error("A voter with this National ID already exists.")
                pause()
                return None

        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
            if age < 18:
                error("You must be at least 18 years old to register.")
                pause()
                return None
        except ValueError:
            error("Invalid date format.")
            pause()
            return None

        gender = prompt("Gender (M/F/Other): ").upper()
        if gender not in ["M", "F", "OTHER"]:
            error("Invalid gender selection.")
            pause()
            return None

        address = prompt("Residential Address: ")
        phone = prompt("Phone Number: ")
        email = prompt("Email Address: ")

        password = masked_input("Create Password: ").strip()
        if len(password) < 6:
            error("Password must be at least 6 characters.")
            pause()
            return None

        confirm_password = masked_input("Confirm Password: ").strip()
        if password != confirm_password:
            error("Passwords do not match.")
            pause()
            return None

        if not stations:
            error("No voting stations available. Contact admin.")
            pause()
            return None

        subheader("Available Voting Stations", "\033[95m")  # THEME_VOTER_ACCENT
        for sid, station in stations.items():
            if station["is_active"]:
                print(f"    \033[94m{sid}.\033[0m {station['name']} \033[2m- {station['location']}\033[0m")

        try:
            station_choice = int(prompt("\nSelect your voting station ID: "))
            if station_choice not in stations or not stations[station_choice]["is_active"]:
                error("Invalid station selection.")
                pause()
                return None
        except ValueError:
            error("Invalid input.")
            pause()
            return None

        voter_card = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

        voter = Voter(
            voter_id_counter, full_name, national_id, dob_str, gender, address,
            phone, email, AuthService.hash_password(password), voter_card,
            station_choice, False, True  # is_verified=False, is_active=True
        )

        print()
        success("Registration successful!")
        print(f"  \033[1mYour Voter Card Number: \033[93m{voter_card}\033[0m")
        warning("IMPORTANT: Save this number! You need it to login.")
        info("Your registration is pending admin verification.")

        return voter


class CandidateService:
    """Service class for candidate operations."""

    @staticmethod
    def create_candidate(candidates: Dict[int, Dict], candidate_id_counter: int, current_user: Admin) -> Optional[Candidate]:
        """Create a new candidate."""
        clear_screen()
        header("CREATE NEW CANDIDATE", "\033[92m")  # THEME_ADMIN
        print()

        full_name = prompt("Full Name: ")
        if not full_name:
            error("Name cannot be empty.")
            pause()
            return None

        national_id = prompt("National ID: ")
        if not national_id:
            error("National ID cannot be empty.")
            pause()
            return None

        # Check for duplicate national ID
        for candidate in candidates.values():
            if candidate["national_id"] == national_id:
                error("A candidate with this National ID already exists.")
                pause()
                return None

        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
        except ValueError:
            error("Invalid date format.")
            pause()
            return None

        gender = prompt("Gender (M/F/Other): ").upper()

        subheader("Education Levels", "\033[33m")  # THEME_ADMIN_ACCENT
        for i, level in enumerate(Candidate.REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    \033[92m{i}.\033[0m {level}")

        try:
            edu_choice = int(prompt("Select education level: "))
            if edu_choice < 1 or edu_choice > len(Candidate.REQUIRED_EDUCATION_LEVELS):
                error("Invalid choice.")
                pause()
                return None
            education = Candidate.REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        except ValueError:
            error("Invalid input.")
            pause()
            return None

        party = prompt("Political Party/Affiliation: ")
        manifesto = prompt("Brief Manifesto/Bio: ")
        address = prompt("Address: ")
        phone = prompt("Phone: ")
        email = prompt("Email: ")

        criminal_record = prompt("Has Criminal Record? (yes/no): ").lower()
        if criminal_record == "yes":
            error("Candidates with criminal records are not eligible.")
            return None

        years_experience = prompt("Years of Public Service/Political Experience: ")
        try:
            years_experience = int(years_experience)
        except ValueError:
            years_experience = 0

        candidate = Candidate(
            candidate_id_counter, full_name, national_id, dob_str, gender,
            education, party, manifesto, address, phone, email, False,
            years_experience, True, True
        )

        if not candidate.is_eligible():
            error("Candidate does not meet eligibility requirements.")
            pause()
            return None

        return candidate


class StationService:
    """Service class for voting station operations."""

    @staticmethod
    def create_station(stations: Dict[int, Dict], station_id_counter: int, current_user: Admin) -> Optional[VotingStation]:
        """Create a new voting station."""
        clear_screen()
        header("CREATE VOTING STATION", "\033[92m")  # THEME_ADMIN
        print()

        name = prompt("Station Name: ")
        if not name:
            error("Name cannot be empty.")
            pause()
            return None

        location = prompt("Location/Address: ")
        if not location:
            error("Location cannot be empty.")
            pause()
            return None

        region = prompt("Region/District: ")

        try:
            capacity = int(prompt("Voter Capacity: "))
            if capacity <= 0:
                error("Capacity must be positive.")
                pause()
                return None
        except ValueError:
            error("Invalid capacity.")
            pause()
            return None

        supervisor = prompt("Station Supervisor Name: ")
        contact = prompt("Contact Phone: ")
        opening_time = prompt("Opening Time (e.g. 08:00): ")
        closing_time = prompt("Closing Time (e.g. 17:00): ")

        station = VotingStation(
            station_id_counter, name, location, region, capacity,
            supervisor, contact, opening_time, closing_time, True
        )

        return station


class PositionService:
    """Service class for position operations."""

    @staticmethod
    def create_position(positions: Dict[int, Dict], position_id_counter: int, current_user: Admin) -> Optional[Position]:
        """Create a new position."""
        clear_screen()
        header("CREATE POSITION", "\033[92m")  # THEME_ADMIN
        print()

        title = prompt("Position Title (e.g. President, Governor, Senator): ")
        if not title:
            error("Title cannot be empty.")
            pause()
            return None

        description = prompt("Description: ")
        level = prompt("Level (National/Regional/Local): ")
        if level.lower() not in ["national", "regional", "local"]:
            error("Invalid level.")
            pause()
            return None

        try:
            max_winners = int(prompt("Number of winners/seats: "))
            if max_winners <= 0:
                error("Must be at least 1.")
                pause()
                return None
        except ValueError:
            error("Invalid number.")
            pause()
            return None

        min_cand_age = prompt(f"Minimum candidate age [{Candidate.MIN_AGE}]: ")
        min_cand_age = int(min_cand_age) if min_cand_age.isdigit() else Candidate.MIN_AGE

        position = Position(
            position_id_counter, title, description, level.capitalize(),
            max_winners, min_cand_age, True
        )

        return position


class PollService:
    """Service class for poll operations."""

    @staticmethod
    def create_poll(polls: Dict[int, Dict], poll_id_counter: int, positions: Dict[int, Dict],
                   stations: Dict[int, Dict], current_user: Admin) -> Optional[Poll]:
        """Create a new poll."""
        clear_screen()
        header("CREATE POLL / ELECTION", "\033[92m")  # THEME_ADMIN
        print()

        title = prompt("Poll/Election Title: ")
        if not title:
            error("Title cannot be empty.")
            pause()
            return None

        description = prompt("Description: ")
        election_type = prompt("Election Type (General/Primary/By-election/Referendum): ")

        start_date = prompt("Start Date (YYYY-MM-DD): ")
        end_date = prompt("End Date (YYYY-MM-DD): ")
        try:
            sd = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            ed = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            if ed <= sd:
                error("End date must be after start date.")
                pause()
                return None
        except ValueError:
            error("Invalid date format.")
            pause()
            return None

        if not positions:
            error("No positions available. Create positions first.")
            pause()
            return None

        subheader("Available Positions", "\033[33m")  # THEME_ADMIN_ACCENT
        active_positions = {pid: p for pid, p in positions.items() if p["is_active"]}
        if not active_positions:
            error("No active positions.")
            pause()
            return None

        for pid, p in active_positions.items():
            print(f"    \033[92m{p['id']}.\033[0m {p['title']} \033[2m({p['level']}) - {p['max_winners']} seat(s)\033[0m")

        try:
            selected_position_ids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
        except ValueError:
            error("Invalid input.")
            pause()
            return None

        poll_positions = []
        for spid in selected_position_ids:
            if spid not in active_positions:
                warning(f"Position ID {spid} not found or inactive. Skipping.")
                continue
            poll_positions.append({
                "position_id": spid,
                "position_title": positions[spid]["title"],
                "candidate_ids": [],
                "max_winners": positions[spid]["max_winners"]
            })

        if not poll_positions:
            error("No valid positions selected.")
            pause()
            return None

        if not stations:
            error("No voting stations. Create stations first.")
            pause()
            return None

        subheader("Available Voting Stations", "\033[33m")  # THEME_ADMIN_ACCENT
        active_stations = {sid: s for sid, s in stations.items() if s["is_active"]}
        for sid, s in active_stations.items():
            print(f"    \033[92m{s['id']}.\033[0m {s['name']} \033[2m({s['location']})\033[0m")

        if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            selected_station_ids = list(active_stations.keys())
        else:
            try:
                selected_station_ids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
            except ValueError:
                error("Invalid input.")
                pause()
                return None

        poll = Poll(
            poll_id_counter, title, description, election_type, start_date,
            end_date, poll_positions, selected_station_ids, "draft"
        )

        return poll


class AuditService:
    """Service class for audit logging."""

    @staticmethod
    def log_action(action: str, user: str, details: str) -> AuditLog:
        """Create an audit log entry."""
        return AuditLog(action, user, details)