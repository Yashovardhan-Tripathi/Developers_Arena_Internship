# The Developers Arena - Python Internship

This repository documents **Yashovardhan Tripathi's six-month Python internship with The Developers Arena**. It contains the monthly projects, their source code, setup instructions, documentation, and supporting internship records.

The Month 1 project is **Complete Personal Productivity Suite**, and the Month 2 project is **TimeConnector**, a Django social media platform. Months 3-6 remain to be completed as part of the internship.

## Internship details

| Detail | Information |
| --- | --- |
| Intern | Yashovardhan Tripathi |
| Organization | The Developers Arena |
| Role | Python Intern |
| Start date | 10 September 2026 |
| Duration | 6 months |
| Work arrangement | Remote / virtual internship |
| Program format | Self-paced learning with monthly deadlines |
| Batch | 10-SEP-2026 - 6M |
| Compensation | Unpaid; training and resources provided |

These details come from the [official internship offer letter](docs/internship/OfferLetter_DevelopersArena.pdf), dated 10 September 2026. The original PDF is included for reference.

## Monthly project progress

| Month | Project | Current progress | Documentation |
| --- | --- | --- | --- |
| 1 | Complete Personal Productivity Suite | Developed; source and documentation available | [Project README](personal_productivity_suite_/README.md) |
| 2 | TimeConnector - Social Media Platform | Developed and verified locally; cloud deployment pending | [Project README](Social%20Media%20Platform%20Django/README.md) |
| 3 | To be added | Pending | Added when the project is available |
| 4 | To be added | Pending | Added when the project is available |
| 5 | To be added | Pending | Added when the project is available |
| 6 | To be added | Pending | Added when the project is available |

This table records project development progress. It does not establish official submission acceptance, evaluation results, or internship completion. The remaining four months' projects and tasks are still to be completed.

## Month 1 - Complete Personal Productivity Suite

A Python command-line application that brings everyday productivity tools into one menu:

- Calculator with arithmetic, expressions, and temporary history.
- Notes manager with JSON storage, search, editing, deletion, and exports.
- Countdown timer and stopwatch with laps.
- File organizer with previews and extension-based categories.
- Unit converter for length, mass, temperature, time, and digital storage.
- Local notes backup and restore.

The application uses Python's standard library at runtime, with pytest for its tests. Its README, Git ignore rules, and Git attributes are kept inside its own project folder.

Explore the [source code](personal_productivity_suite_/), [project README](personal_productivity_suite_/README.md), [detailed guide](personal_productivity_suite_/GUIDE.md), and [screenshots](personal_productivity_suite_/docs/screenshots/README.md).

## Month 2 - TimeConnector

A Django social media platform with:

- Account registration, authentication, and member profiles.
- Text and image posts, likes, comments, and audience controls.
- Friend requests, following, blocking, and privacy protections.
- Search, notifications, and live WebSocket updates.
- Authenticated REST APIs and staff moderation tools.
- A responsive Bootstrap interface and automated tests.

The project documents local verification in its own README. Cloud deployment is pending; this repository does not claim a live production deployment.

Explore the [source code](Social%20Media%20Platform%20Django/), [project README](Social%20Media%20Platform%20Django/README.md), and [functionality audit](Social%20Media%20Platform%20Django/docs/FUNCTIONAL_AUDIT.md).

## Repository structure

```text
Developers_Arena_Internship/
|-- README.md                         # Internship overview and monthly progress
|-- docs/
|   `-- internship/
|       `-- OfferLetter_DevelopersArena.pdf
|-- personal_productivity_suite_/      # Month 1
|   |-- README.md
|   |-- GUIDE.md
|   |-- .gitignore
|   |-- .gitattributes
|   |-- main.py
|   |-- docs/
|   `-- tests/
`-- Social Media Platform Django/     # Month 2: TimeConnector
    |-- README.md
    |-- manage.py
    |-- docs/
    `-- tests/
```

Months 3-6 will be documented here when their projects are added.

## Getting started

Clone the repository:

```powershell
git clone https://github.com/Yashovardhan-Tripathi/Developers_Arena_Internship.git
cd Developers_Arena_Internship
```

Follow the setup instructions for the project you want to run:

- [Month 1: Productivity Suite setup](personal_productivity_suite_/README.md#project-and-launch)
- [Month 2: TimeConnector setup](Social%20Media%20Platform%20Django/README.md#quick-start-windows-powershell)

Each project has its own dependencies, configuration, and verification instructions.

## Learning and completion requirements

The offer letter describes a program built around learning modules, practical projects, monthly task submissions, progress tracking, and review feedback. Evaluation considers task completion and quality, code quality and best practices, project implementation and documentation, and learning progress.

The letter states that certificate eligibility requires completion of **80% of tasks with satisfactory evaluations**. This task-based requirement is separate from the monthly project table above; the table does not calculate certificate eligibility. The internship is ongoing, and no completion certificate or final evaluation is claimed here.

The offer letter also states that internship work remains the property of The Developers Arena unless otherwise specified in writing. This repository does not grant a separate license to that work.

## Supporting document

[View the official internship offer letter (PDF)](docs/internship/OfferLetter_DevelopersArena.pdf)

The letter is the source for the program details and conditions. The monthly project mapping and remaining work reflect the intern's current progress.
