import datetime
import hashlib
import json
import os
from typing import Dict, List, Optional, Any


class DataManager:
    """Handles data persistence operations."""

    DATA_FILE = "evoting_data.json"

    @staticmethod
    def save_data(data: Dict[str, Any]) -> None:
        """Save data to JSON file."""
        try:
            with open(DataManager.DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    @staticmethod
    def load_data() -> Dict[str, Any]:
        """Load data from JSON file."""
        try:
            if os.path.exists(DataManager.DATA_FILE):
                with open(DataManager.DATA_FILE, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
        return {}


class User:
    """Base user class."""

    def __init__(self, user_id: int, full_name: str, email: str, password_hash: str, is_active: bool = True):
        self.id = user_id
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.created_at = datetime.datetime.now()

    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "password": self.password_hash,
            "is_active": self.is_active,
            "created_at": str(self.created_at)
        }


class Admin(User):
    """Admin user class."""

    def __init__(self, user_id: int, username: str, full_name: str, email: str, password_hash: str,
                 role: str = "admin", is_active: bool = True):
        super().__init__(user_id, full_name, email, password_hash, is_active)
        self.username = username
        self.role = role

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "username": self.username,
            "role": self.role
        })
        return data


class Voter(User):
    """Voter user class."""

    MIN_AGE = 18

    def __init__(self, user_id: int, full_name: str, national_id: str, date_of_birth: str,
                 gender: str, address: str, phone: str, email: str, password_hash: str,
                 voter_card_number: str, station_id: int, is_verified: bool = False,
                 is_active: bool = True):
        super().__init__(user_id, full_name, email, password_hash, is_active)
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = self._calculate_age()
        self.gender = gender
        self.address = address
        self.phone = phone
        self.voter_card_number = voter_card_number
        self.station_id = station_id
        self.is_verified = is_verified
        self.has_voted_in: List[int] = []
        self.registered_at = datetime.datetime.now()

    def _calculate_age(self) -> int:
        """Calculate age from date of birth."""
        dob = datetime.datetime.strptime(self.date_of_birth, "%Y-%m-%d")
        return (datetime.datetime.now() - dob).days // 365

    def can_vote(self) -> bool:
        """Check if voter can vote."""
        return self.is_active and self.is_verified and self.age >= self.MIN_AGE

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "national_id": self.national_id,
            "date_of_birth": self.date_of_birth,
            "age": self.age,
            "gender": self.gender,
            "address": self.address,
            "phone": self.phone,
            "voter_card_number": self.voter_card_number,
            "station_id": self.station_id,
            "is_verified": self.is_verified,
            "has_voted_in": self.has_voted_in,
            "registered_at": str(self.registered_at)
        })
        return data


class Candidate:
    """Candidate class."""

    MIN_AGE = 25
    MAX_AGE = 75
    REQUIRED_EDUCATION_LEVELS = ["Bachelor's Degree", "Master's Degree", "PhD", "Doctorate"]

    def __init__(self, candidate_id: int, full_name: str, national_id: str, date_of_birth: str,
                 gender: str, education: str, party: str, manifesto: str, address: str,
                 phone: str, email: str, has_criminal_record: bool, years_experience: int,
                 is_active: bool = True, is_approved: bool = True):
        self.id = candidate_id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = self._calculate_age()
        self.gender = gender
        self.education = education
        self.party = party
        self.manifesto = manifesto
        self.address = address
        self.phone = phone
        self.email = email
        self.has_criminal_record = has_criminal_record
        self.years_experience = years_experience
        self.is_active = is_active
        self.is_approved = is_approved
        self.created_at = datetime.datetime.now()

    def _calculate_age(self) -> int:
        """Calculate age from date of birth."""
        dob = datetime.datetime.strptime(self.date_of_birth, "%Y-%m-%d")
        return (datetime.datetime.now() - dob).days // 365

    def is_eligible(self) -> bool:
        """Check if candidate is eligible."""
        return (self.MIN_AGE <= self.age <= self.MAX_AGE and
                not self.has_criminal_record and
                self.education in self.REQUIRED_EDUCATION_LEVELS)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "national_id": self.national_id,
            "date_of_birth": self.date_of_birth,
            "age": self.age,
            "gender": self.gender,
            "education": self.education,
            "party": self.party,
            "manifesto": self.manifesto,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "has_criminal_record": self.has_criminal_record,
            "years_experience": self.years_experience,
            "is_active": self.is_active,
            "is_approved": self.is_approved,
            "created_at": str(self.created_at)
        }


class VotingStation:
    """Voting station class."""

    def __init__(self, station_id: int, name: str, location: str, region: str,
                 capacity: int, supervisor: str, contact: str, opening_time: str,
                 closing_time: str, is_active: bool = True):
        self.id = station_id
        self.name = name
        self.location = location
        self.region = region
        self.capacity = capacity
        self.registered_voters = 0  # This will be calculated dynamically
        self.supervisor = supervisor
        self.contact = contact
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.is_active = is_active
        self.created_at = datetime.datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "region": self.region,
            "capacity": self.capacity,
            "registered_voters": self.registered_voters,
            "supervisor": self.supervisor,
            "contact": self.contact,
            "opening_time": self.opening_time,
            "closing_time": self.closing_time,
            "is_active": self.is_active,
            "created_at": str(self.created_at)
        }


class Position:
    """Election position class."""

    def __init__(self, position_id: int, title: str, description: str, level: str,
                 max_winners: int, min_candidate_age: int, is_active: bool = True):
        self.id = position_id
        self.title = title
        self.description = description
        self.level = level
        self.max_winners = max_winners
        self.min_candidate_age = min_candidate_age
        self.is_active = is_active
        self.created_at = datetime.datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "level": self.level,
            "max_winners": self.max_winners,
            "min_candidate_age": self.min_candidate_age,
            "is_active": self.is_active,
            "created_at": str(self.created_at)
        }


class Poll:
    """Election poll class."""

    def __init__(self, poll_id: int, title: str, description: str, election_type: str,
                 start_date: str, end_date: str, positions: List[Dict], station_ids: List[int],
                 status: str = "draft"):
        self.id = poll_id
        self.title = title
        self.description = description
        self.election_type = election_type
        self.start_date = start_date
        self.end_date = end_date
        self.positions = positions  # List of dicts with position_id, candidate_ids, etc.
        self.station_ids = station_ids
        self.status = status  # draft, open, closed
        self.total_votes_cast = 0
        self.created_at = datetime.datetime.now()

    def is_active(self) -> bool:
        """Check if poll is currently active."""
        now = datetime.datetime.now().date()
        start = datetime.datetime.strptime(self.start_date, "%Y-%m-%d").date()
        end = datetime.datetime.strptime(self.end_date, "%Y-%m-%d").date()
        return self.status == "open" and start <= now <= end

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "election_type": self.election_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "positions": self.positions,
            "station_ids": self.station_ids,
            "status": self.status,
            "total_votes_cast": self.total_votes_cast,
            "created_at": str(self.created_at)
        }


class Vote:
    """Vote record class."""

    def __init__(self, voter_id: int, poll_id: int, position_id: int, candidate_id: int,
              timestamp: Optional[datetime.datetime] = None):
        self.voter_id = voter_id
        self.poll_id = poll_id
        self.position_id = position_id
        self.candidate_id = candidate_id
        self.timestamp = timestamp or datetime.datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "voter_id": self.voter_id,
            "poll_id": self.poll_id,
            "position_id": self.position_id,
            "candidate_id": self.candidate_id,
            "timestamp": str(self.timestamp)
        }


class AuditLog:
    """Audit log entry class."""

    def __init__(self, action: str, user: str, details: str, timestamp: Optional[datetime.datetime] = None):
        self.timestamp = timestamp or datetime.datetime.now()
        self.action = action
        self.user = user
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": str(self.timestamp),
            "action": self.action,
            "user": self.user,
            "details": self.details
        }