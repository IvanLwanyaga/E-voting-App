my readme file   # E-Voting System Application

## Overview

The **E-Voting System** is a console-based electronic voting application designed to manage secure and transparent elections. The system allows administrators to manage elections, candidates, voters, and voting stations, while enabling voters to securely cast votes.

The application follows modern **software engineering principles**, including Object-Oriented Design (OOd), Clean Code practices, and Separation of Concerns (SoC) to ensure maintainability, scalability, and readability.

---

# System Architecture

The application follows a **layered architecture** that separates responsibilities into distinct modules.

```
Application Layer
     │
     ▼
Service Layer
     │
     ▼
Model Layer
     │
     ▼
Data Storage Layer
```

## 1. Application Layer

**File:** `main.py`

This layer controls the main workflow of the application.

Responsibilities:

* User authentication flow
* Dashboard navigation
* System orchestration
* Calling services to perform operations

Main Class:

```
EVotingApp
```

---

## 2. Service Layer

The service layer contains the **business logic** of the application.

Services include:

* `AuthService`
* `CandidateService`
* `StationService`
* `PositionService`
* `PollService`
* `AuditService`

Responsibilities:

* Authentication
* Candidate management
* Poll management
* Station management
* Audit logging
* System validation

This layer ensures that **business rules are separated from the user interface**.

---

## 3. Model Layer

The model layer defines the **data structures and entities** used in the system.

Key models:

* `User`
* `Admin`
* `Voter`
* `Candidate`
* `VotingStation`
* `Position`
* `Poll`
* `Vote`
* `AuditLog`

Responsibilities:

* Represent system entities
* Provide data validation
* Convert objects to dictionaries for storage

---

## 4. UI Layer

The UI module handles **all user interactions**.

Responsibilities:

* Menu rendering
* User prompts
* Screen formatting
* Input handling

Examples of UI utilities:

* `header()`
* `prompt()`
* `masked_input()`
* `error()`
* `success()`

This keeps **presentation logic separate from business logic**.

---

## 5. Data Management Layer

The system uses a **DataManager** class for data persistence.

Responsibilities:

* Loading application data
* Saving system state
* Maintaining system counters

Stored data includes:

* voters
* candidates
* stations
* polls
* votes
* administrators
* audit logs

---

# Object-Oriented Design

The application implements key OOP principles.

## Encapsulation

Classes encapsulate both data and behavior.

Example:

```
class EVotingApp
```

This class manages the application's workflow and system state.

---

## Abstraction

Complex operations are abstracted through service classes.

Example:

```
AuthService.login_admin()
CandidateService.create_candidate()
PollService.create_poll()
```

This hides implementation details from the main application.

---

## Modularity

The application is divided into modules:

```
models/
services/
ui/
main.py
```

This improves maintainability and readability.

---

# Clean Code Principles

The project follows several Clean Code practices.

### Meaningful Naming

Examples:

* `create_candidate()`
* `view_all_voters()`
* `assign_candidates_to_poll()`

These names clearly describe their functionality.

---

### Single Responsibility Principle

Each method performs **one specific task**.

Examples:

* `create_poll()`
* `update_station()`
* `verify_voter()`

---

### Code Readability

The code uses:

* consistent indentation
* descriptive variables
* modular methods
* structured menus

This improves readability and maintainability.

---

# Security Features

The system implements several security mechanisms.

### Password Security

Passwords are stored using **hashed values**.

```
AuthService.hash_password()
```

---

### Role-Based Access Control

Users are divided into roles:

* **Admin**
* **Voter**

Each role has different system permissions.

---

### Audit Logging

Every important action is recorded in the audit log.

Examples:

* Login attempts
* Candidate creation
* Poll management
* Voter verification

This improves system transparency and accountability.

---

# Key Features

### Admin Features

* Create and manage candidates
* Manage voting stations
* Create election polls
* Assign candidates to positions
* Manage voters
* Verify voters
* View election results
* View system statistics
* View audit logs

---

### Voter Features

* Secure login
* View available polls
* Cast votes
* View voting history
* Update personal profile
* Change password

---

# System Benefits

The application provides:

* Secure election management
* Transparent voting process
* Structured system architecture
* Maintainable codebase
* Modular design

# Future Improvements

Possible future improvements include:

* Web-based interface
* Database integration (PostgreSQL / MySQL)
* Blockchain voting verification
* Biometric voter authentication
* Real-time election analytics


# Authors

LWANYAGA IVAN
TUMUSIME JULIUS
MUCHUNGUZI GODFREY
JOHN PAUL
