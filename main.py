import datetime
import hashlib
import random
import string
from typing import Dict, List, Optional, Any
from models import (
    DataManager, User, Admin, Voter, Candidate, VotingStation,
    Position, Poll, Vote, AuditLog
)
from ui import UI, Colors, clear_screen, pause, prompt, masked_input, error, success, warning, info, subheader, header, table_header, table_divider, menu_item, status_badge
from services import (
    AuthService, CandidateService, StationService, PositionService,
    PollService, AuditService
)


class EVotingApp:
    """Main application class for the E-Voting System."""

    def __init__(self):
        self.data_manager = DataManager()
        self.current_user = None
        self.current_role = None

        # Load data
        self.load_data()

    def load_data(self) -> None:
        """Load application data from storage."""
        data = self.data_manager.load_data()

        # Initialize data structures
        self.candidates = {int(k): v for k, v in data.get("candidates", {}).items()}
        self.candidate_id_counter = data.get("candidate_id_counter", 1)

        self.voting_stations = {int(k): v for k, v in data.get("voting_stations", {}).items()}
        self.station_id_counter = data.get("station_id_counter", 1)

        self.polls = {int(k): v for k, v in data.get("polls", {}).items()}
        self.poll_id_counter = data.get("poll_id_counter", 1)

        self.positions = {int(k): v for k, v in data.get("positions", {}).items()}
        self.position_id_counter = data.get("position_id_counter", 1)

        self.voters = {int(k): v for k, v in data.get("voters", {}).items()}
        self.voter_id_counter = data.get("voter_id_counter", 1)

        self.admins = {int(k): v for k, v in data.get("admins", {}).items()}
        self.admin_id_counter = data.get("admin_id_counter", 1)

        self.votes = data.get("votes", [])
        self.audit_log = [AuditLog(a["action"], a["user"], a["details"],
                                   datetime.datetime.fromisoformat(a["timestamp"]))
                         for a in data.get("audit_log", [])]

        # Initialize default admin if not exists
        if not self.admins:
            default_admin = Admin(
                1, "admin", "System Administrator", "admin@evote.com",
                AuthService.hash_password("admin123"), "super_admin", True
            )
            self.admins[1] = default_admin.to_dict()
            self.admin_id_counter = 2

    def save_data(self) -> None:
        """Save application data to storage."""
        data = {
            "candidates": self.candidates,
            "candidate_id_counter": self.candidate_id_counter,
            "voting_stations": self.voting_stations,
            "station_id_counter": self.station_id_counter,
            "polls": self.polls,
            "poll_id_counter": self.poll_id_counter,
            "positions": self.positions,
            "position_id_counter": self.position_id_counter,
            "voters": self.voters,
            "voter_id_counter": self.voter_id_counter,
            "admins": self.admins,
            "admin_id_counter": self.admin_id_counter,
            "votes": self.votes,
            "audit_log": [log.to_dict() for log in self.audit_log]
        }
        self.data_manager.save_data(data)

    def log_action(self, action: str, user: str, details: str) -> None:
        """Log an audit action."""
        audit_entry = AuditService.log_action(action, user, details)
        self.audit_log.append(audit_entry)

    def run(self) -> None:
        """Main application loop."""
        while True:
            if not self.login():
                break

            if self.current_role == "admin":
                self.admin_dashboard()
            elif self.current_role == "voter":
                self.voter_dashboard()

    def login(self) -> bool:
        """Handle user login."""
        UI.display_welcome()
        choice = UI.display_login_menu()

        if choice == "1":  # Admin login
            clear_screen()
            header("ADMIN LOGIN", Colors.THEME_ADMIN)
            print()
            username = prompt("Username: ")
            password = masked_input("Password: ").strip()

            admin = AuthService.login_admin(self.admins, username, password)
            if admin:
                self.current_user = admin
                self.current_role = "admin"
                self.log_action("LOGIN", username, "Admin login successful")
                print()
                success(f"Welcome, {admin.full_name}!")
                pause()
                return True
            else:
                error("Invalid credentials.")
                self.log_action("LOGIN_FAILED", username, "Invalid admin credentials")
                pause()
                return False

        elif choice == "2":  # Voter login
            clear_screen()
            header("VOTER LOGIN", Colors.THEME_VOTER)
            print()
            voter_card = prompt("Voter Card Number: ")
            password = masked_input("Password: ").strip()

            voter = AuthService.login_voter(self.voters, voter_card, password)
            if voter:
                self.current_user = voter
                self.current_role = "voter"
                self.log_action("LOGIN", voter_card, "Voter login successful")
                print()
                success(f"Welcome, {voter.full_name}!")
                pause()
                return True
            else:
                error("Invalid voter card number or password.")
                self.log_action("LOGIN_FAILED", voter_card, "Invalid voter credentials")
                pause()
                return False

        elif choice == "3":  # Register voter
            voter = AuthService.register_voter(self.voters, self.voter_id_counter, self.voting_stations)
            if voter:
                self.voters[self.voter_id_counter] = voter.to_dict()
                self.log_action("REGISTER", voter.full_name, f"New voter registered with card: {voter.voter_card_number}")
                self.voter_id_counter += 1
                self.save_data()
            return False

        elif choice == "4":  # Exit
            print()
            info("Goodbye!")
            self.save_data()
            return False

        else:
            error("Invalid choice.")
            pause()
            return False

    def admin_dashboard(self) -> None:
        """Admin dashboard loop."""
        while True:
            choice = UI.display_admin_dashboard(self.current_user.full_name, self.current_user.role)

            if choice == "1": self.create_candidate()
            elif choice == "2": self.view_all_candidates()
            elif choice == "3": self.update_candidate()
            elif choice == "4": self.delete_candidate()
            elif choice == "5": self.search_candidates()
            elif choice == "6": self.create_voting_station()
            elif choice == "7": self.view_all_stations()
            elif choice == "8": self.update_station()
            elif choice == "9": self.delete_station()
            elif choice == "10": self.create_position()
            elif choice == "11": self.view_positions()
            elif choice == "12": self.update_position()
            elif choice == "13": self.delete_position()
            elif choice == "14": self.create_poll()
            elif choice == "15": self.view_all_polls()
            elif choice == "16": self.update_poll()
            elif choice == "17": self.delete_poll()
            elif choice == "18": self.open_close_poll()
            elif choice == "19": self.assign_candidates_to_poll()
            elif choice == "20": self.view_all_voters()
            elif choice == "21": self.verify_voter()
            elif choice == "22": self.deactivate_voter()
            elif choice == "23": self.search_voters()
            elif choice == "24": self.create_admin()
            elif choice == "25": self.view_admins()
            elif choice == "26": self.deactivate_admin()
            elif choice == "27": self.view_poll_results()
            elif choice == "28": self.view_detailed_statistics()
            elif choice == "29": self.view_audit_log()
            elif choice == "30": self.station_wise_results()
            elif choice == "31": self.save_data(); pause()
            elif choice == "32":
                self.log_action("LOGOUT", self.current_user.username, "Admin logged out")
                self.save_data()
                break
            else:
                error("Invalid choice.")
                pause()

    def voter_dashboard(self) -> None:
        """Voter dashboard loop."""
        while True:
            choice = UI.display_voter_dashboard(self.current_user.full_name)

            if choice == "1": self.view_available_polls()
            elif choice == "2": self.cast_vote()
            elif choice == "3": self.view_voting_history()
            elif choice == "4": self.view_profile()
            elif choice == "5": self.update_profile()
            elif choice == "6": self.change_password()
            elif choice == "7":
                self.log_action("LOGOUT", self.current_user.voter_card_number, "Voter logged out")
                break
            else:
                error("Invalid choice.")
                pause()

    # Candidate management methods
    def create_candidate(self) -> None:
        candidate = CandidateService.create_candidate(self.candidates, self.candidate_id_counter, self.current_user)
        if candidate:
            self.candidates[self.candidate_id_counter] = candidate.to_dict()
            self.log_action("CREATE_CANDIDATE", self.current_user.username,  f"Created candidate: {candidate.full_name} (ID: {self.candidate_id_counter})")
            print()
            success(f"Candidate '{candidate.full_name}' created successfully! ID: {self.candidate_id_counter}")
            self.candidate_id_counter += 1
            self.save_data()
        pause()

    def view_all_candidates(self) -> None:
        clear_screen()
        header("ALL CANDIDATES", Colors.THEME_ADMIN)
        if not self.candidates:
            print()
            info("No candidates found.")
            pause()
            return

        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}", Colors.THEME_ADMIN)
        table_divider(85, Colors.THEME_ADMIN)

        for cid, c in self.candidates.items():
            status = status_badge("Active", True) if c["is_active"] else status_badge("Inactive", False)
            print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20} {status}")

        print(f"\n  {Colors.DIM}Total Candidates: {len(self.candidates)}{Colors.RESET}")
        pause()

    def update_candidate(self) -> None:
        clear_screen()
        header("UPDATE CANDIDATE", Colors.THEME_ADMIN)
        if not self.candidates:
            print()
            info("No candidates found.")
            pause()
            return

        print()
        for cid, c in self.candidates.items():
            print(f"  {Colors.THEME_ADMIN}{c['id']}.{Colors.RESET} {c['full_name']} {Colors.DIM}({c['party']}){Colors.RESET}")

        try:
            cid = int(prompt("\nEnter Candidate ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if cid not in self.candidates:
            error("Candidate not found.")
            pause()
            return

        c = self.candidates[cid]
        print(f"\n  {Colors.BOLD}Updating: {c['full_name']}{Colors.RESET}")
        info("Press Enter to keep current value\n")

        new_name = prompt(f"Full Name [{c['full_name']}]: ")
        if new_name: c["full_name"] = new_name

        new_party = prompt(f"Party [{c['party']}]: ")
        if new_party: c["party"] = new_party

        new_manifesto = prompt(f"Manifesto [{c['manifesto'][:50]}...]: ")
        if new_manifesto: c["manifesto"] = new_manifesto

        new_phone = prompt(f"Phone [{c['phone']}]: ")
        if new_phone: c["phone"] = new_phone

        new_email = prompt(f"Email [{c['email']}]: ")
        if new_email: c["email"] = new_email

        new_address = prompt(f"Address [{c['address']}]: ")
        if new_address: c["address"] = new_address

        new_exp = prompt(f"Years Experience [{c['years_experience']}]: ")
        if new_exp:
            try:
                c["years_experience"] = int(new_exp)
            except ValueError:
                warning("Invalid number, keeping old value.")

        self.log_action("UPDATE_CANDIDATE", self.current_user.username, f"Updated candidate: {c['full_name']} (ID: {cid})")
        print()
        success(f"Candidate '{c['full_name']}' updated successfully!")
        self.save_data()
        pause()

    def delete_candidate(self) -> None:
        clear_screen()
        header("DELETE CANDIDATE", Colors.THEME_ADMIN)
        if not self.candidates:
            print()
            info("No candidates found.")
            pause()
            return

        print()
        for cid, c in self.candidates.items():
            status = status_badge("Active", True) if c["is_active"] else status_badge("Inactive", False)
            print(f"  {Colors.THEME_ADMIN}{c['id']}.{Colors.RESET} {c['full_name']} {Colors.DIM}({c['party']}){Colors.RESET} {status}")

        try:
            cid = int(prompt("\nEnter Candidate ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if cid not in self.candidates:
            error("Candidate not found.")
            pause()
            return

        # Check if candidate is in active polls
        for pid, poll in self.polls.items():
            if poll["status"] == "open":
                for pos in poll.get("positions", []):
                    if cid in pos.get("candidate_ids", []):
                        error(f"Cannot delete - candidate is in active poll: {poll['title']}")
                        pause()
                        return

        confirm = prompt(f"Are you sure you want to delete '{self.candidates[cid]['full_name']}'? (yes/no): ").lower()
        if confirm == "yes":
            deleted_name = self.candidates[cid]["full_name"]
            self.candidates[cid]["is_active"] = False
            self.log_action("DELETE_CANDIDATE", self.current_user.username, f"Deactivated candidate: {deleted_name} (ID: {cid})")
            print()
            success(f"Candidate '{deleted_name}' has been deactivated.")
            self.save_data()
        else:
            info("Deletion cancelled.")
        pause()

    def search_candidates(self) -> None:
        clear_screen()
        header("SEARCH CANDIDATES", Colors.THEME_ADMIN)
        subheader("Search by", Colors.THEME_ADMIN_ACCENT)
        menu_item(1, "Name", Colors.THEME_ADMIN)
        menu_item(2, "Party", Colors.THEME_ADMIN)
        menu_item(3, "Education Level", Colors.THEME_ADMIN)
        menu_item(4, "Age Range", Colors.THEME_ADMIN)
        choice = prompt("\nChoice: ")

        results = []
        if choice == "1":
            term = prompt("Enter name to search: ").lower()
            results = [c for c in self.candidates.values() if term in c["full_name"].lower()]
        elif choice == "2":
            term = prompt("Enter party name: ").lower()
            results = [c for c in self.candidates.values() if term in c["party"].lower()]
        elif choice == "3":
            subheader("Education Levels", Colors.THEME_ADMIN_ACCENT)
            for i, level in enumerate(Candidate.REQUIRED_EDUCATION_LEVELS, 1):
                print(f"    {Colors.THEME_ADMIN}{i}.{Colors.RESET} {level}")
            try:
                edu_choice = int(prompt("Select: "))
                edu = Candidate.REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
                results = [c for c in self.candidates.values() if c["education"] == edu]
            except (ValueError, IndexError):
                error("Invalid choice.")
                pause()
                return
        elif choice == "4":
            try:
                min_age = int(prompt("Min age: "))
                max_age = int(prompt("Max age: "))
                results = [c for c in self.candidates.values() if min_age <= c["age"] <= max_age]
            except ValueError:
                error("Invalid input.")
                pause()
                return
        else:
            error("Invalid choice.")
            pause()
            return

        if not results:
            print()
            info("No candidates found matching your criteria.")
        else:
            print(f"\n  {Colors.BOLD}Found {len(results)} candidate(s):{Colors.RESET}")
            table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}", Colors.THEME_ADMIN)
            table_divider(75, Colors.THEME_ADMIN)
            for c in results:
                print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20}")
        pause()

    # Station management methods
    def create_voting_station(self) -> None:
        station = StationService.create_station(self.voting_stations, self.station_id_counter, self.current_user)
        if station:
            self.voting_stations[self.station_id_counter] = station.to_dict()
            self.log_action("CREATE_STATION", self.current_user.username,
                           f"Created station: {station.name} (ID: {self.station_id_counter})")
            print()
            success(f"Voting Station '{station.name}' created! ID: {self.station_id_counter}")
            self.station_id_counter += 1
            self.save_data()
        pause()

    def view_all_stations(self) -> None:
        clear_screen()
        header("ALL VOTING STATIONS", Colors.THEME_ADMIN)
        if not self.voting_stations:
            print()
            info("No voting stations found.")
            pause()
            return

        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}", Colors.THEME_ADMIN)
        table_divider(96, Colors.THEME_ADMIN)

        for sid, s in self.voting_stations.items():
            reg_count = sum(1 for v in self.voters.values() if v["station_id"] == sid)
            status = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
            print(f"  {s['id']:<5} {s['name']:<25} {s['location']:<25} {s['region']:<15} {s['capacity']:<8} {reg_count:<8} {status}")

        print(f"\n  {Colors.DIM}Total Stations: {len(self.voting_stations)}{Colors.RESET}")
        pause()

    def update_station(self) -> None:
        clear_screen()
        header("UPDATE VOTING STATION", Colors.THEME_ADMIN)
        if not self.voting_stations:
            print()
            info("No stations found.")
            pause()
            return

        print()
        for sid, s in self.voting_stations.items():
            print(f"  {Colors.THEME_ADMIN}{s['id']}.{Colors.RESET} {s['name']} {Colors.DIM}- {s['location']}{Colors.RESET}")

        try:
            sid = int(prompt("\nEnter Station ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if sid not in self.voting_stations:
            error("Station not found.")
            pause()
            return

        s = self.voting_stations[sid]
        print(f"\n  {Colors.BOLD}Updating: {s['name']}{Colors.RESET}")
        info("Press Enter to keep current value\n")

        new_name = prompt(f"Name [{s['name']}]: ")
        if new_name: s["name"] = new_name

        new_location = prompt(f"Location [{s['location']}]: ")
        if new_location: s["location"] = new_location

        new_region = prompt(f"Region [{s['region']}]: ")
        if new_region: s["region"] = new_region

        new_capacity = prompt(f"Capacity [{s['capacity']}]: ")
        if new_capacity:
            try:
                s["capacity"] = int(new_capacity)
            except ValueError:
                warning("Invalid number, keeping old value.")

        new_supervisor = prompt(f"Supervisor [{s['supervisor']}]: ")
        if new_supervisor: s["supervisor"] = new_supervisor

        new_contact = prompt(f"Contact [{s['contact']}]: ")
        if new_contact: s["contact"] = new_contact

        self.log_action("UPDATE_STATION", self.current_user.username, f"Updated station: {s['name']} (ID: {sid})")
        print()
        success(f"Station '{s['name']}' updated successfully!")
        self.save_data()
        pause()

    def delete_station(self) -> None:
        clear_screen()
        header("DELETE VOTING STATION", Colors.THEME_ADMIN)
        if not self.voting_stations:
            print()
            info("No stations found.")
            pause()
            return

        print()
        for sid, s in self.voting_stations.items():
            status = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
            print(f"  {Colors.THEME_ADMIN}{s['id']}.{Colors.RESET} {s['name']} {Colors.DIM}({s['location']}){Colors.RESET} {status}")

        try:
            sid = int(prompt("\nEnter Station ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if sid not in self.voting_stations:
            error("Station not found.")
            pause()
            return

        voter_count = sum(1 for v in self.voters.values() if v["station_id"] == sid)
        if voter_count > 0:
            warning(f"{voter_count} voters are registered at this station.")
            if prompt("Proceed with deactivation? (yes/no): ").lower() != "yes":
                info("Cancelled.")
                pause()
                return

        if prompt(f"Confirm deactivation of '{self.voting_stations[sid]['name']}'? (yes/no): ").lower() == "yes":
            self.voting_stations[sid]["is_active"] = False
            self.log_action("DELETE_STATION", self.current_user.username, f"Deactivated station: {self.voting_stations[sid]['name']}")
            print()
            success(f"Station '{self.voting_stations[sid]['name']}' deactivated.")
            self.save_data()
        else:
            info("Cancelled.")
        pause()

    # Position management methods
    def create_position(self) -> None:
        position = PositionService.create_position(self.positions, self.position_id_counter, self.current_user)
        if position:
            self.positions[self.position_id_counter] = position.to_dict()
            self.log_action("CREATE_POSITION", self.current_user.username,
                           f"Created position: {position.title} (ID: {self.position_id_counter})")
            print()
            success(f"Position '{position.title}' created! ID: {self.position_id_counter}")
            self.position_id_counter += 1
            self.save_data()
        pause()

    def view_positions(self) -> None:
        clear_screen()
        header("ALL POSITIONS", Colors.THEME_ADMIN)
        if not self.positions:
            print()
            info("No positions found.")
            pause()
            return

        print()
        table_header(f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}", Colors.THEME_ADMIN)
        table_divider(70, Colors.THEME_ADMIN)

        for pid, p in self.positions.items():
            status = status_badge("Active", True) if p["is_active"] else status_badge("Inactive", False)
            print(f"  {p['id']:<5} {p['title']:<25} {p['level']:<12} {p['max_winners']:<8} {p['min_candidate_age']:<10} {status}")

        print(f"\n  {Colors.DIM}Total Positions: {len(self.positions)}{Colors.RESET}")
        pause()

    def update_position(self) -> None:
        clear_screen()
        header("UPDATE POSITION", Colors.THEME_ADMIN)
        if not self.positions:
            print()
            info("No positions found.")
            pause()
            return

        print()
        for pid, p in self.positions.items():
            print(f"  {Colors.THEME_ADMIN}{p['id']}.{Colors.RESET} {p['title']} {Colors.DIM}({p['level']}){Colors.RESET}")

        try:
            pid = int(prompt("\nEnter Position ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if pid not in self.positions:
            error("Position not found.")
            pause()
            return

        p = self.positions[pid]
        print(f"\n  {Colors.BOLD}Updating: {p['title']}{Colors.RESET}")
        info("Press Enter to keep current value\n")

        new_title = prompt(f"Title [{p['title']}]: ")
        if new_title: p["title"] = new_title

        new_desc = prompt(f"Description [{p['description'][:50]}]: ")
        if new_desc: p["description"] = new_desc

        new_level = prompt(f"Level [{p['level']}]: ")
        if new_level and new_level.lower() in ["national", "regional", "local"]:
            p["level"] = new_level.capitalize()

        new_seats = prompt(f"Seats [{p['max_winners']}]: ")
        if new_seats:
            try:
                p["max_winners"] = int(new_seats)
            except ValueError:
                warning("Keeping old value.")

        self.log_action("UPDATE_POSITION", self.current_user.username, f"Updated position: {p['title']}")
        print()
        success("Position updated!")
        self.save_data()
        pause()

    def delete_position(self) -> None:
        clear_screen()
        header("DELETE POSITION", Colors.THEME_ADMIN)
        if not self.positions:
            print()
            info("No positions found.")
            pause()
            return

        print()
        for pid, p in self.positions.items():
            print(f"  {Colors.THEME_ADMIN}{p['id']}.{Colors.RESET} {p['title']} {Colors.DIM}({p['level']}){Colors.RESET}")

        try:
            pid = int(prompt("\nEnter Position ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if pid not in self.positions:
            error("Position not found.")
            pause()
            return

        # Check if position is in active polls
        for poll_id, poll in self.polls.items():
            for pp in poll.get("positions", []):
                if pp["position_id"] == pid and poll["status"] == "open":
                    error(f"Cannot delete - in active poll: {poll['title']}")
                    pause()
                    return

        if prompt(f"Confirm deactivation of '{self.positions[pid]['title']}'? (yes/no): ").lower() == "yes":
            self.positions[pid]["is_active"] = False
            self.log_action("DELETE_POSITION", self.current_user.username, f"Deactivated position: {self.positions[pid]['title']}")
            print()
            success("Position deactivated.")
            self.save_data()
        pause()

    # Poll management methods
    def create_poll(self) -> None:
        poll = PollService.create_poll(self.polls, self.poll_id_counter, self.positions, self.voting_stations, self.current_user)
        if poll:
            self.polls[self.poll_id_counter] = poll.to_dict()
            self.log_action("CREATE_POLL", self.current_user.username,
                           f"Created poll: {poll.title} (ID: {self.poll_id_counter})")
            print()
            success(f"Poll '{poll.title}' created! ID: {self.poll_id_counter}")
            warning("Status: DRAFT - Assign candidates and then open the poll.")
            self.poll_id_counter += 1
            self.save_data()
        pause()

    def view_all_polls(self) -> None:
        clear_screen()
        header("ALL POLLS / ELECTIONS", Colors.THEME_ADMIN)
        if not self.polls:
            print()
            info("No polls found.")
            pause()
            return

        for pid, poll in self.polls.items():
            sc = Colors.GREEN if poll['status'] == 'open' else (Colors.YELLOW if poll['status'] == 'draft' else Colors.RED)
            print(f"\n  {Colors.BOLD}{Colors.THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{Colors.RESET}")
            print(f"  {Colors.DIM}Type:{Colors.RESET} {poll['election_type']}  {Colors.DIM}│  Status:{Colors.RESET} {sc}{Colors.BOLD}{poll['status'].upper()}{Colors.RESET}")
            print(f"  {Colors.DIM}Period:{Colors.RESET} {poll['start_date']} to {poll['end_date']}  {Colors.DIM}│  Votes:{Colors.RESET} {poll['total_votes_cast']}")
            for pos in poll["positions"]:
                cand_names = [self.candidates[ccid]["full_name"] for ccid in pos["candidate_ids"] if ccid in self.candidates]
                cand_display = ', '.join(cand_names) if cand_names else f"{Colors.DIM}None assigned{Colors.RESET}"
                print(f"    {Colors.THEME_ADMIN_ACCENT}▸{Colors.RESET} {pos['position_title']}: {cand_display}")
        print(f"\n  {Colors.DIM}Total Polls: {len(self.polls)}{Colors.RESET}")
        pause()

    def update_poll(self) -> None:
        clear_screen()
        header("UPDATE POLL", Colors.THEME_ADMIN)
        if not self.polls:
            print()
            info("No polls found.")
            pause()
            return

        print()
        for pid, poll in self.polls.items():
            sc = Colors.GREEN if poll['status'] == 'open' else (Colors.YELLOW if poll['status'] == 'draft' else Colors.RED)
            print(f"  {Colors.THEME_ADMIN}{poll['id']}.{Colors.RESET} {poll['title']} {sc}({poll['status']}){Colors.RESET}")

        try:
            pid = int(prompt("\nEnter Poll ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if pid not in self.polls:
            error("Poll not found.")
            pause()
            return

        poll = self.polls[pid]
        if poll["status"] == "open":
            error("Cannot update an open poll. Close it first.")
            pause()
            return

        if poll["status"] == "closed" and poll["total_votes_cast"] > 0:
            error("Cannot update a poll with votes.")
            pause()
            return

        print(f"\n  {Colors.BOLD}Updating: {poll['title']}{Colors.RESET}")
        info("Press Enter to keep current value\n")

        new_title = prompt(f"Title [{poll['title']}]: ")
        if new_title: poll["title"] = new_title

        new_desc = prompt(f"Description [{poll['description'][:50]}]: ")
        if new_desc: poll["description"] = new_desc

        new_type = prompt(f"Election Type [{poll['election_type']}]: ")
        if new_type: poll["election_type"] = new_type

        new_start = prompt(f"Start Date [{poll['start_date']}]: ")
        if new_start:
            try:
                datetime.datetime.strptime(new_start, "%Y-%m-%d")
                poll["start_date"] = new_start
            except ValueError:
                warning("Invalid date, keeping old value.")

        new_end = prompt(f"End Date [{poll['end_date']}]: ")
        if new_end:
            try:
                datetime.datetime.strptime(new_end, "%Y-%m-%d")
                poll["end_date"] = new_end
            except ValueError:
                warning("Invalid date, keeping old value.")

        self.log_action("UPDATE_POLL", self.current_user.username, f"Updated poll: {poll['title']}")
        print()
        success("Poll updated!")
        self.save_data()
        pause()

    def delete_poll(self) -> None:
        clear_screen()
        header("DELETE POLL", Colors.THEME_ADMIN)
        if not self.polls:
            print()
            info("No polls found.")
            pause()
            return

        print()
        for pid, poll in self.polls.items():
            print(f"  {Colors.THEME_ADMIN}{poll['id']}.{Colors.RESET} {poll['title']} {Colors.DIM}({poll['status']}){Colors.RESET}")

        try:
            pid = int(prompt("\nEnter Poll ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if pid not in self.polls:
            error("Poll not found.")
            pause()
            return

        # Check if poll has votes
        if self.polls[pid]["total_votes_cast"] > 0:
            error("Cannot delete a poll with votes.")
            pause()
            return

        if prompt(f"Confirm deletion of '{self.polls[pid]['title']}'? (yes/no): ").lower() == "yes":
            deleted_title = self.polls[pid]["title"]
            del self.polls[pid]
            self.log_action("DELETE_POLL", self.current_user.username, f"Deleted poll: {deleted_title}")
            print()
            success("Poll deleted.")
            self.save_data()
        pause()

    def open_close_poll(self) -> None:
        clear_screen()
        header("OPEN/CLOSE POLL", Colors.THEME_ADMIN)
        if not self.polls:
            print()
            info("No polls found.")
            pause()
            return

        print()
        for pid, poll in self.polls.items():
            sc = Colors.GREEN if poll['status'] == 'open' else (Colors.YELLOW if poll['status'] == 'draft' else Colors.RED)
            print(f"  {Colors.THEME_ADMIN}{poll['id']}.{Colors.RESET} {poll['title']} {sc}({poll['status']}){Colors.RESET}")

        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if pid not in self.polls:
            error("Poll not found.")
            pause()
            return

        poll = self.polls[pid]

        if poll["status"] == "draft":
            # Check if candidates are assigned
            has_candidates = False
            for pos in poll["positions"]:
                if pos["candidate_ids"]:
                    has_candidates = True
                    break

            if not has_candidates:
                error("Cannot open poll - no candidates assigned to positions.")
                pause()
                return

            if prompt(f"Open poll '{poll['title']}'? (yes/no): ").lower() == "yes":
                poll["status"] = "open"
                self.log_action("OPEN_POLL", self.current_user.username, f"Opened poll: {poll['title']}")
                success("Poll opened successfully!")
                self.save_data()

        elif poll["status"] == "open":
            if prompt(f"Close poll '{poll['title']}'? (yes/no): ").lower() == "yes":
                poll["status"] = "closed"
                self.log_action("CLOSE_POLL", self.current_user.username, f"Closed poll: {poll['title']}")
                success("Poll closed successfully!")
                self.save_data()

        else:
            error("Poll is already closed.")
        pause()

    def assign_candidates_to_poll(self) -> None:
        clear_screen()
        header("ASSIGN CANDIDATES TO POLL", Colors.THEME_ADMIN)
        if not self.polls:
            print()
            info("No polls found.")
            pause()
            return

        print()
        draft_polls = {pid: p for pid, p in self.polls.items() if p["status"] == "draft"}
        if not draft_polls:
            error("No draft polls available for candidate assignment.")
            pause()
            return

        for pid, poll in draft_polls.items():
            print(f"  {Colors.THEME_ADMIN}{poll['id']}.{Colors.RESET} {poll['title']}")

        try:
            pid = int(prompt("\nSelect Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if pid not in draft_polls:
            error("Invalid poll selection.")
            pause()
            return

        poll = self.polls[pid]

        if not self.candidates:
            error("No candidates available.")
            pause()
            return

        active_candidates = {cid: c for cid, c in self.candidates.items() if c["is_active"] and c["is_approved"]}

        for pos in poll["positions"]:
            print(f"\n  {Colors.BOLD}Position: {pos['position_title']}{Colors.RESET}")
            print("  Available Candidates:")

            eligible_candidates = []
            for cid, c in active_candidates.items():
                if c["age"] >= self.positions[pos["position_id"]]["min_candidate_age"]:
                    eligible_candidates.append((cid, c))

            if not eligible_candidates:
                warning("No eligible candidates for this position.")
                continue

            for cid, c in eligible_candidates:
                assigned = "✓" if cid in pos["candidate_ids"] else " "
                print(f"    {Colors.THEME_ADMIN}{cid}.{Colors.RESET} [{assigned}] {c['full_name']} ({c['party']})")

            try:
                cids_str = prompt(f"Enter candidate IDs for {pos['position_title']} (comma-separated): ")
                if cids_str.strip():
                    selected_cids = [int(x.strip()) for x in cids_str.split(",")]
                    valid_cids = [cid for cid in selected_cids if cid in active_candidates and cid in [c[0] for c in eligible_candidates]]
                    pos["candidate_ids"] = valid_cids
                    success(f"Assigned {len(valid_cids)} candidates to {pos['position_title']}")
                else:
                    pos["candidate_ids"] = []
                    info("Cleared candidates for this position.")
            except ValueError:
                warning("Invalid input, keeping current assignments.")

        self.log_action("ASSIGN_CANDIDATES", self.current_user.username, f"Assigned candidates to poll: {poll['title']}")
        success("Candidate assignments updated!")
        self.save_data()
        pause()

    # Voter management methods
    def view_all_voters(self) -> None:
        clear_screen()
        header("ALL VOTERS", Colors.THEME_ADMIN)
        if not self.voters:
            print()
            info("No voters found.")
            pause()
            return

        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Card':<15} {'Station':<10} {'Verified':<10} {'Active':<8}", Colors.THEME_ADMIN)
        table_divider(73, Colors.THEME_ADMIN)

        for vid, v in self.voters.items():
            station_name = self.voting_stations.get(v["station_id"], {}).get("name", "Unknown")
            verified = status_badge("Yes", True) if v["is_verified"] else status_badge("No", False)
            active = status_badge("Yes", True) if v["is_active"] else status_badge("No", False)
            print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {station_name:<10} {verified:<10} {active:<8}")

        print(f"\n  {Colors.DIM}Total Voters: {len(self.voters)}{Colors.RESET}")
        pause()

    def verify_voter(self) -> None:
        clear_screen()
        header("VERIFY VOTER", Colors.THEME_ADMIN)
        if not self.voters:
            print()
            info("No voters found.")
            pause()
            return

        print()
        unverified_voters = {vid: v for vid, v in self.voters.items() if not v["is_verified"] and v["is_active"]}
        if not unverified_voters:
            info("All active voters are already verified.")
            pause()
            return

        for vid, v in unverified_voters.items():
            station_name = self.voting_stations.get(v["station_id"], {}).get("name", "Unknown")
            print(f"  {Colors.THEME_ADMIN}{v['id']}.{Colors.RESET} {v['full_name']} {Colors.DIM}({v['voter_card_number']}) - {station_name}{Colors.RESET}")

        try:
            vid = int(prompt("\nEnter Voter ID to verify: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if vid not in unverified_voters:
            error("Invalid voter selection.")
            pause()
            return

        if prompt(f"Verify voter '{unverified_voters[vid]['full_name']}'? (yes/no): ").lower() == "yes":
            self.voters[vid]["is_verified"] = True
            self.log_action("VERIFY_VOTER", self.current_user.username, f"Verified voter: {unverified_voters[vid]['full_name']}")
            success("Voter verified successfully!")
            self.save_data()
        else:
            info("Verification cancelled.")
        pause()

    def deactivate_voter(self) -> None:
        clear_screen()
        header("DEACTIVATE VOTER", Colors.THEME_ADMIN)
        if not self.voters:
            print()
            info("No voters found.")
            pause()
            return

        print()
        for vid, v in self.voters.items():
            status = status_badge("Active", True) if v["is_active"] else status_badge("Inactive", False)
            print(f"  {Colors.THEME_ADMIN}{v['id']}.{Colors.RESET} {v['full_name']} {Colors.DIM}({v['voter_card_number']}){Colors.RESET} {status}")

        try:
            vid = int(prompt("\nEnter Voter ID to deactivate: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if vid not in self.voters:
            error("Voter not found.")
            pause()
            return

        voter = self.voters[vid]
        if not voter["is_active"]:
            error("Voter is already inactive.")
            pause()
            return

        if prompt(f"Deactivate voter '{voter['full_name']}'? (yes/no): ").lower() == "yes":
            self.voters[vid]["is_active"] = False
            self.log_action("DEACTIVATE_VOTER", self.current_user.username, f"Deactivated voter: {voter['full_name']}")
            success("Voter deactivated successfully!")
            self.save_data()
        else:
            info("Deactivation cancelled.")
        pause()

    def search_voters(self) -> None:
        clear_screen()
        header("SEARCH VOTERS", Colors.THEME_ADMIN)
        subheader("Search by", Colors.THEME_ADMIN_ACCENT)
        menu_item(1, "Name", Colors.THEME_ADMIN)
        menu_item(2, "Voter Card Number", Colors.THEME_ADMIN)
        menu_item(3, "National ID", Colors.THEME_ADMIN)
        choice = prompt("\nChoice: ")

        results = []
        if choice == "1":
            term = prompt("Enter name to search: ").lower()
            results = [v for v in self.voters.values() if term in v["full_name"].lower()]
        elif choice == "2":
            term = prompt("Enter voter card number: ").upper()
            results = [v for v in self.voters.values() if term in v["voter_card_number"]]
        elif choice == "3":
            term = prompt("Enter national ID: ")
            results = [v for v in self.voters.values() if term in v["national_id"]]
        else:
            error("Invalid choice.")
            pause()
            return

        if not results:
            print()
            info("No voters found matching your criteria.")
        else:
            print(f"\n  {Colors.BOLD}Found {len(results)} voter(s):{Colors.RESET}")
            table_header(f"{'ID':<5} {'Name':<25} {'Card':<15} {'Verified':<10} {'Active':<8}", Colors.THEME_ADMIN)
            table_divider(63, Colors.THEME_ADMIN)
            for v in results:
                verified = status_badge("Yes", True) if v["is_verified"] else status_badge("No", False)
                active = status_badge("Yes", True) if v["is_active"] else status_badge("No", False)
                print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {verified:<10} {active:<8}")
        pause()

    # Admin management methods
    def create_admin(self) -> None:
        clear_screen()
        header("CREATE ADMIN ACCOUNT", Colors.THEME_ADMIN)
        print()

        username = prompt("Username: ")
        if not username:
            error("Username cannot be empty.")
            pause()
            return

        # Check for duplicate username
        for admin in self.admins.values():
            if admin["username"] == username:
                error("Username already exists.")
                pause()
                return

        full_name = prompt("Full Name: ")
        if not full_name:
            error("Name cannot be empty.")
            pause()
            return

        email = prompt("Email: ")
        role = prompt("Role (admin/super_admin): ")
        if role not in ["admin", "super_admin"]:
            error("Invalid role.")
            pause()
            return

        password = masked_input("Create Password: ").strip()
        if len(password) < 6:
            error("Password must be at least 6 characters.")
            pause()
            return

        confirm_password = masked_input("Confirm Password: ").strip()
        if password != confirm_password:
            error("Passwords do not match.")
            pause()
            return

        admin = Admin(
            self.admin_id_counter, username, full_name, email,
            AuthService.hash_password(password), role, True
        )

        self.admins[self.admin_id_counter] = admin.to_dict()
        self.log_action("CREATE_ADMIN", self.current_user.username, f"Created admin: {username}")
        print()
        success(f"Admin account '{username}' created successfully!")
        self.admin_id_counter += 1
        self.save_data()
        pause()

    def view_admins(self) -> None:
        clear_screen()
        header("ALL ADMINS", Colors.THEME_ADMIN)
        if not self.admins:
            print()
            info("No admins found.")
            pause()
            return

        print()
        table_header(f"{'ID':<5} {'Username':<15} {'Name':<25} {'Role':<15} {'Active':<8}", Colors.THEME_ADMIN)
        table_divider(68, Colors.THEME_ADMIN)

        for aid, a in self.admins.items():
            active = status_badge("Yes", True) if a["is_active"] else status_badge("No", False)
            print(f"  {a['id']:<5} {a['username']:<15} {a['full_name']:<25} {a['role']:<15} {active:<8}")

        print(f"\n  {Colors.DIM}Total Admins: {len(self.admins)}{Colors.RESET}")
        pause()

    def deactivate_admin(self) -> None:
        clear_screen()
        header("DEACTIVATE ADMIN", Colors.THEME_ADMIN)
        if not self.admins:
            print()
            info("No admins found.")
            pause()
            return

        print()
        for aid, a in self.admins.items():
            if a["id"] != self.current_user.id:  # Can't deactivate self
                active = status_badge("Active", True) if a["is_active"] else status_badge("Inactive", False)
                print(f"  {Colors.THEME_ADMIN}{a['id']}.{Colors.RESET} {a['username']} {Colors.DIM}({a['full_name']}){Colors.RESET} {active}")

        try:
            aid = int(prompt("\nEnter Admin ID to deactivate: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if aid not in self.admins or aid == self.current_user.id:
            error("Invalid admin selection.")
            pause()
            return

        admin = self.admins[aid]
        if not admin["is_active"]:
            error("Admin is already inactive.")
            pause()
            return

        if prompt(f"Deactivate admin '{admin['username']}'? (yes/no): ").lower() == "yes":
            self.admins[aid]["is_active"] = False
            self.log_action("DEACTIVATE_ADMIN", self.current_user.username, f"Deactivated admin: {admin['username']}")
            success("Admin deactivated successfully!")
            self.save_data()
        else:
            info("Deactivation cancelled.")
        pause()

    # Results and reports methods
    def view_poll_results(self) -> None:
        clear_screen()
        header("POLL RESULTS", Colors.THEME_ADMIN)
        if not self.polls:
            print()
            info("No polls found.")
            pause()
            return

        print()
        closed_polls = {pid: p for pid, p in self.polls.items() if p["status"] == "closed"}
        if not closed_polls:
            info("No closed polls available.")
            pause()
            return

        for pid, poll in closed_polls.items():
            print(f"  {Colors.THEME_ADMIN}{poll['id']}.{Colors.RESET} {poll['title']} {Colors.DIM}({poll['total_votes_cast']} votes){Colors.RESET}")

        try:
            pid = int(prompt("\nSelect Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if pid not in closed_polls:
            error("Invalid poll selection.")
            pause()
            return

        poll = self.polls[pid]
        print(f"\n  {Colors.BOLD}{Colors.THEME_ADMIN}Results for: {poll['title']}{Colors.RESET}")
        print(f"  {Colors.DIM}Total Votes Cast: {poll['total_votes_cast']}{Colors.RESET}\n")

        for pos in poll["positions"]:
            print(f"  {Colors.THEME_ADMIN_ACCENT}Position: {pos['position_title']} ({pos['max_winners']} seat(s)){Colors.RESET}")

            # Count votes for this position
            position_votes = [v for v in self.votes if v["poll_id"] == pid and v["position_id"] == pos["position_id"]]
            candidate_vote_counts = {}

            for cid in pos["candidate_ids"]:
                if cid in self.candidates:
                    candidate_vote_counts[cid] = 0

            for vote in position_votes:
                if vote["candidate_id"] in candidate_vote_counts:
                    candidate_vote_counts[vote["candidate_id"]] += 1

            # Sort by vote count descending
            sorted_candidates = sorted(candidate_vote_counts.items(), key=lambda x: x[1], reverse=True)

            if sorted_candidates:
                table_header(f"{'Rank':<6} {'Candidate':<25} {'Party':<20} {'Votes':<8} {'%':<6}", Colors.THEME_ADMIN)
                table_divider(65, Colors.THEME_ADMIN)

                for rank, (cid, votes) in enumerate(sorted_candidates, 1):
                    candidate = self.candidates[cid]
                    percentage = (votes / len(position_votes) * 100) if position_votes else 0
                    winner_mark = "🏆" if rank <= pos["max_winners"] else ""
                    print(f"  {rank:<6} {candidate['full_name']:<25} {candidate['party']:<20} {votes:<8} {percentage:<6.1f}{winner_mark}")
            else:
                info("No votes recorded for this position.")

            print()
        pause()

    def view_detailed_statistics(self) -> None:
        clear_screen()
        header("DETAILED STATISTICS", Colors.THEME_ADMIN)

        total_voters = len(self.voters)
        verified_voters = sum(1 for v in self.voters.values() if v["is_verified"])
        active_voters = sum(1 for v in self.voters.values() if v["is_active"])

        total_candidates = len(self.candidates)
        active_candidates = sum(1 for c in self.candidates.values() if c["is_active"])

        total_stations = len(self.voting_stations)
        active_stations = sum(1 for s in self.voting_stations.values() if s["is_active"])

        total_polls = len(self.polls)
        open_polls = sum(1 for p in self.polls.values() if p["status"] == "open")
        closed_polls = sum(1 for p in self.polls.values() if p["status"] == "closed")

        total_votes = len(self.votes)

        print(f"\n  {Colors.THEME_ADMIN_ACCENT}Voters:{Colors.RESET}")
        print(f"    Total: {total_voters}")
        print(f"    Verified: {verified_voters} ({verified_voters/total_voters*100:.1f}%)" if total_voters else f"    Verified: {verified_voters}")
        print(f"    Active: {active_voters} ({active_voters/total_voters*100:.1f}%)" if total_voters else f"    Active: {active_voters}")

        print(f"\n  {Colors.THEME_ADMIN_ACCENT}Candidates:{Colors.RESET}")
        print(f"    Total: {total_candidates}")
        print(f"    Active: {active_candidates} ({active_candidates/total_candidates*100:.1f}%)" if total_candidates else f"    Active: {active_candidates}")

        print(f"\n  {Colors.THEME_ADMIN_ACCENT}Stations:{Colors.RESET}")
        print(f"    Total: {total_stations}")
        print(f"    Active: {active_stations} ({active_stations/total_stations*100:.1f}%)" if total_stations else f"    Active: {active_stations}")

        print(f"\n  {Colors.THEME_ADMIN_ACCENT}Polls:{Colors.RESET}")
        print(f"    Total: {total_polls}")
        print(f"    Open: {open_polls}")
        print(f"    Closed: {closed_polls}")

        print(f"\n  {Colors.THEME_ADMIN_ACCENT}Votes:{Colors.RESET}")
        print(f"    Total Votes Cast: {total_votes}")

        if self.polls:
            print(f"\n  {Colors.THEME_ADMIN_ACCENT}Poll Details:{Colors.RESET}")
            for pid, poll in self.polls.items():
                status_color = Colors.GREEN if poll['status'] == 'open' else (Colors.YELLOW if poll['status'] == 'draft' else Colors.RED)
                print(f"    {poll['title']}: {status_color}{poll['status'].upper()}{Colors.RESET} ({poll['total_votes_cast']} votes)")

        pause()

    def view_audit_log(self) -> None:
        clear_screen()
        header("AUDIT LOG", Colors.THEME_ADMIN)
        if not self.audit_log:
            print()
            info("No audit logs found.")
            pause()
            return

        print()
        table_header(f"{'Timestamp':<20} {'Action':<20} {'User':<15} {'Details':<50}", Colors.THEME_ADMIN)
        table_divider(105, Colors.THEME_ADMIN)

        # Show last 50 entries
        for log in self.audit_log[-50:]:
            timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            details = log.details[:47] + "..." if len(log.details) > 47 else log.details
            print(f"  {timestamp:<20} {log.action:<20} {log.user:<15} {details:<50}")

        print(f"\n  {Colors.DIM}Showing last {min(50, len(self.audit_log))} of {len(self.audit_log)} entries{Colors.RESET}")
        pause()

    def station_wise_results(self) -> None:
        clear_screen()
        header("STATION-WISE RESULTS", Colors.THEME_ADMIN)
        if not self.polls:
            print()
            info("No polls found.")
            pause()
            return

        print()
        closed_polls = {pid: p for pid, p in self.polls.items() if p["status"] == "closed"}
        if not closed_polls:
            info("No closed polls available.")
            pause()
            return

        for pid, poll in closed_polls.items():
            print(f"  {Colors.THEME_ADMIN}{poll['id']}.{Colors.RESET} {poll['title']}")

        try:
            pid = int(prompt("\nSelect Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        if pid not in closed_polls:
            error("Invalid poll selection.")
            pause()
            return

        poll = self.polls[pid]
        print(f"\n  {Colors.BOLD}{Colors.THEME_ADMIN}Station-wise Results for: {poll['title']}{Colors.RESET}\n")

        for sid in poll["station_ids"]:
            if sid not in self.voting_stations:
                continue

            station = self.voting_stations[sid]
            station_votes = [v for v in self.votes if v["poll_id"] == pid and self.voters.get(v["voter_id"], {}).get("station_id") == sid]

            print(f"  {Colors.THEME_ADMIN_ACCENT}Station: {station['name']} ({station['location']}){Colors.RESET}")
            print(f"    Votes Cast: {len(station_votes)}")

            if station_votes:
                for pos in poll["positions"]:
                    pos_votes = [v for v in station_votes if v["position_id"] == pos["position_id"]]
                    if pos_votes:
                        print(f"      {pos['position_title']}: {len(pos_votes)} votes")
            print()
        pause()

    # Voter methods
    def view_available_polls(self) -> None:
        clear_screen()
        header("AVAILABLE POLLS", Colors.THEME_VOTER)

        available_polls = []
        for poll in self.polls.values():
            if poll["status"] == "open":
                now = datetime.datetime.now().date()
                start = datetime.datetime.strptime(poll["start_date"], "%Y-%m-%d").date()
                end = datetime.datetime.strptime(poll["end_date"], "%Y-%m-%d").date()
                if start <= now <= end:
                    available_polls.append(poll)

        if not available_polls:
            print()
            info("No polls are currently available for voting.")
            pause()
            return

        for poll in available_polls:
            print(f"\n  {Colors.BOLD}{Colors.THEME_VOTER}Poll #{poll['id']}: {poll['title']}{Colors.RESET}")
            print(f"  {Colors.DIM}Type:{Colors.RESET} {poll['election_type']}")
            print(f"  {Colors.DIM}Period:{Colors.RESET} {poll['start_date']} to {poll['end_date']}")

            # Check if voter has voted in this poll
            has_voted = poll['id'] in self.current_user.has_voted_in
            status = status_badge("VOTED", True) if has_voted else status_badge("NOT VOTED", False)
            print(f"  {Colors.DIM}Status:{Colors.RESET} {status}")

            for pos in poll["positions"]:
                cand_names = [self.candidates[ccid]["full_name"] for ccid in pos["candidate_ids"] if ccid in self.candidates]
                print(f"    {Colors.THEME_VOTER_ACCENT}▸{Colors.RESET} {pos['position_title']}: {len(cand_names)} candidates")

        pause()

    def cast_vote(self) -> None:
        clear_screen()
        header("CAST VOTE", Colors.THEME_VOTER)

        available_polls = []
        for poll in self.polls.values():
            if (poll["status"] == "open" and
                poll['id'] not in self.current_user.has_voted_in and
                self.current_user.station_id in poll["station_ids"]):
                now = datetime.datetime.now().date()
                start = datetime.datetime.strptime(poll["start_date"], "%Y-%m-%d").date()
                end = datetime.datetime.strptime(poll["end_date"], "%Y-%m-%d").date()
                if start <= now <= end:
                    available_polls.append(poll)

        if not available_polls:
            print()
            info("No polls are currently available for you to vote in.")
            pause()
            return

        print()
        for poll in available_polls:
            print(f"  {Colors.THEME_VOTER}{poll['id']}.{Colors.RESET} {poll['title']}")

        try:
            pid = int(prompt("\nSelect Poll ID to vote in: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        poll = next((p for p in available_polls if p["id"] == pid), None)
        if not poll:
            error("Invalid poll selection.")
            pause()
            return

        print(f"\n  {Colors.BOLD}Voting in: {poll['title']}{Colors.RESET}")
        print(f"  {Colors.DIM}Election Type: {poll['election_type']}{Colors.RESET}\n")

        votes_cast = []

        for pos in poll["positions"]:
            print(f"  {Colors.THEME_VOTER_ACCENT}Position: {pos['position_title']}{Colors.RESET}")
            print("  Candidates:")

            candidates = [(cid, self.candidates[cid]) for cid in pos["candidate_ids"] if cid in self.candidates]
            if not candidates:
                warning(f"No candidates available for {pos['position_title']}. Skipping.")
                continue

            for i, (cid, c) in enumerate(candidates, 1):
                print(f"    {Colors.THEME_VOTER}{i}.{Colors.RESET} {c['full_name']} ({c['party']})")
                print(f"       {Colors.DIM}{c['manifesto'][:100]}...{Colors.RESET}")

            try:
                choice = int(prompt(f"\nSelect candidate for {pos['position_title']} (1-{len(candidates)}): "))
                if 1 <= choice <= len(candidates):
                    selected_cid = candidates[choice - 1][0]
                    votes_cast.append({
                        "position_id": pos["position_id"],
                        "candidate_id": selected_cid
                    })
                    success(f"Voted for {self.candidates[selected_cid]['full_name']}")
                else:
                    error("Invalid choice.")
                    return
            except ValueError:
                error("Invalid input.")
                return

        if prompt("\nConfirm and submit your votes? (yes/no): ").lower() == "yes":
            for vote_data in votes_cast:
                vote = Vote(self.current_user.id, poll["id"], vote_data["position_id"], vote_data["candidate_id"])
                self.votes.append(vote.to_dict())

            self.current_user.has_voted_in.append(poll["id"])
            self.voters[self.current_user.id]["has_voted_in"] = self.current_user.has_voted_in
            self.polls[poll["id"]]["total_votes_cast"] += 1

            self.log_action("VOTE_CAST", self.current_user.voter_card_number, f"Voted in poll: {poll['title']}")
            success("Your votes have been recorded successfully!")
            self.save_data()
        else:
            info("Voting cancelled.")

        pause()

    def view_voting_history(self) -> None:
        clear_screen()
        header("VOTING HISTORY", Colors.THEME_VOTER)

        voter_votes = [v for v in self.votes if v["voter_id"] == self.current_user.id]

        if not voter_votes:
            print()
            info("You haven't cast any votes yet.")
            pause()
            return

        print()
        for vote in voter_votes:
            poll = self.polls.get(vote["poll_id"])
            if not poll:
                continue

            candidate = self.candidates.get(vote["candidate_id"])
            position = next((p for p in poll["positions"] if p["position_id"] == vote["position_id"]), None)

            if candidate and position:
                timestamp = datetime.datetime.fromisoformat(vote["timestamp"])
                print(f"  {Colors.THEME_VOTER_ACCENT}Poll:{Colors.RESET} {poll['title']}")
                print(f"  {Colors.DIM}Position:{Colors.RESET} {position['position_title']}")
                print(f"  {Colors.DIM}Candidate:{Colors.RESET} {candidate['full_name']} ({candidate['party']})")
                print(f"  {Colors.DIM}Timestamp:{Colors.RESET} {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print()

        pause()

    def view_profile(self) -> None:
        clear_screen()
        header("VOTER PROFILE", Colors.THEME_VOTER)

        v = self.voters[self.current_user.id]
        station = self.voting_stations.get(v["station_id"], {})

        print(f"\n  {Colors.BOLD}Full Name:{Colors.RESET} {v['full_name']}")
        print(f"  {Colors.BOLD}National ID:{Colors.RESET} {v['national_id']}")
        print(f"  {Colors.BOLD}Date of Birth:{Colors.RESET} {v['date_of_birth']} (Age: {v['age']})")
        print(f"  {Colors.BOLD}Gender:{Colors.RESET} {v['gender']}")
        print(f"  {Colors.BOLD}Address:{Colors.RESET} {v['address']}")
        print(f"  {Colors.BOLD}Phone:{Colors.RESET} {v['phone']}")
        print(f"  {Colors.BOLD}Email:{Colors.RESET} {v['email']}")
        print(f"  {Colors.BOLD}Voter Card:{Colors.RESET} {v['voter_card_number']}")
        print(f"  {Colors.BOLD}Voting Station:{Colors.RESET} {station.get('name', 'Unknown')} ({station.get('location', 'Unknown')})")
        print(f"  {Colors.BOLD}Verified:{Colors.RESET} {status_badge('Yes', True) if v['is_verified'] else status_badge('No', False)}")
        print(f"  {Colors.BOLD}Active:{Colors.RESET} {status_badge('Yes', True) if v['is_active'] else status_badge('No', False)}")
        print(f"  {Colors.BOLD}Registered:{Colors.RESET} {v['registered_at']}")

        pause()

    def update_profile(self) -> None:
        clear_screen()
        header("UPDATE PROFILE", Colors.THEME_VOTER)

        v = self.voters[self.current_user.id]
        print(f"\n  {Colors.BOLD}Updating: {v['full_name']}{Colors.RESET}")
        info("Press Enter to keep current value\n")

        new_address = prompt(f"Address [{v['address']}]: ")
        if new_address: v["address"] = new_address

        new_phone = prompt(f"Phone [{v['phone']}]: ")
        if new_phone: v["phone"] = new_phone

        new_email = prompt(f"Email [{v['email']}]: ")
        if new_email: v["email"] = new_email

        self.log_action("UPDATE_PROFILE", self.current_user.voter_card_number, "Updated profile")
        print()
        success("Profile updated successfully!")
        self.save_data()
        pause()

    def change_password(self) -> None:
        clear_screen()
        header("CHANGE PASSWORD", Colors.THEME_VOTER)
        print()

        current_password = masked_input("Current Password: ").strip()
        if not self.current_user.verify_password(current_password):
            error("Current password is incorrect.")
            pause()
            return

        new_password = masked_input("New Password: ").strip()
        if len(new_password) < 6:
            error("Password must be at least 6 characters.")
            pause()
            return

        confirm_password = masked_input("Confirm New Password: ").strip()
        if new_password != confirm_password:
            error("Passwords do not match.")
            pause()
            return

        self.voters[self.current_user.id]["password"] = AuthService.hash_password(new_password)
        self.current_user.password_hash = AuthService.hash_password(new_password)

        self.log_action("CHANGE_PASSWORD", self.current_user.voter_card_number, "Changed password")
        success("Password changed successfully!")
        self.save_data()
        pause()


if __name__ == "__main__":
    app = EVotingApp()
    app.run()