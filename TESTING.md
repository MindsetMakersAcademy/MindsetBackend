Why tests exist here
--------------------
This repository contains a mix of unit and integration tests. The primary goal
for the test suite is to provide fast, deterministic checks that the public
behaviour of the application is correct. We prioritize testing the "top layer"
(services and HTTP-facing API endpoints) because these are the behaviours that
matter most to callers and because they exercise the glue between layers
(repository, models, and DTOs).

High-level testing flow
------------------------
1. Tests live under `tests/` and are grouped by purpose:
   - `tests/unit/` — fast unit tests that exercise service logic in isolation.
   - `tests/integration/` — higher-level tests using the Flask test client to
     exercise HTTP endpoints and input/output shapes.

2. Shared test helpers and fakes are declared in `tests/conftest.py`. We use
   small, dict-backed fake repositories to keep unit tests fast and deterministic
   while still validating DTO (Pydantic) conversions.

3. Services accept session and repository dependencies so tests inject fakes or
   tiny session-like objects. This allows tests to focus on behaviour rather
   than on SQLAlchemy internals.

4. API integration tests use the Flask test client fixture (`client`) and set
   up module-level service bindings (the test `client` fixture replaces the
   module-level service in `app.api.v1.course` with a test service bound to
   fake repos). This keeps the application factory simple while still letting
   integration tests exercise the HTTP surface.

Why top-layer tests first
-------------------------
- They validate the behaviour users of the service actually observe (DTO
  shapes, endpoints, error codes).
- They exercise the integration between components (services + DTOS + repo
  contracts) which catches a different class of bugs than low-level unit
  tests.
- Low-level repository tests are still valuable — especially for migrations or
  complex query logic — but they are postponed until we need to test SQL
  code paths specifically. For many day-to-day development tasks, verifying
  the top-layer behaviour gives faster feedback and higher confidence.

Fixtures and typing
-------------------
- Common fixtures (fake repos, dummy session objects, Flask `client`) live in
  `tests/conftest.py`.
- To reduce noise from type checkers, tests use `tests/pyrightconfig.json` to
  relax type checking under the `tests/` folder. A lightweight `TestSession`
  protocol is defined in `conftest.py` for typing fixtures without pulling in
  heavy SQLAlchemy types.

Writing new tests — checklist
----------------------------
- Decide unit vs integration. If you only need to verify pure business logic
  use unit tests under `tests/unit/`. If you want to exercise HTTP behaviour
  or DTO serialization, prefer `tests/integration/`.
- Add a short docstring (1–2 lines) to each test describing the scenario being
  validated.
- Use existing fixtures where possible:
  - `fake_*` repositories for fast unit tests
  - `dummy_session` when a session-like object is required
  - `client` for integration tests
- Keep tests deterministic. Seed deterministic data via fixtures and avoid
  relying on the system clock or network.
- Aim for clear, small assertions — one or two things per test.

Running tests
-------------
- Run the full suite locally:

```bash
pytest
```

- Run a single module or file:

```bash
pytest tests/unit/services/test_course_service.py -q
```

Link from README
----------------
The README contains a pointer to this document for further reading.
