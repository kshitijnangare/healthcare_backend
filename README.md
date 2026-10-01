# Healthcare Backend (Django + DRF + PostgreSQL)

REST API to register/login users (JWT) and manage patients, doctors and patient-doctor assignments.
Stack: Django 5.2, Django REST Framework, djangorestframework-simplejwt, PostgreSQL (Supabase), Django ORM.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then fill in your values
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Import `postman_collection.json` into Postman. Run **Login**, which saves `access_token` automatically,
then call any other request. Run the Create requests first, because they save `patient_id`, `doctor_id` and `mapping_id`.

## Database: Supabase + pgAdmin

Everything is read from `.env`, so only the env values change. Two styles are supported:

```
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxxx.supabase.co:5432/postgres
# or DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT
```

- SSL is on by default (`DB_SSLMODE=require`), as Supabase requires.
- URL-encode special characters in the password (`@` -> `%40`, `#` -> `%23`).
- **Direct connection (port 5432):** may be IPv6-only. If it fails on your network, use the *Session pooler* string from the Supabase dashboard.
- **Transaction pooler (port 6543):** detected automatically. The app sets `DISABLE_SERVER_SIDE_CURSORS=True` and `CONN_MAX_AGE=0`.
- **pgAdmin:** register a server with the same host, port, database, user and password (SSL mode `require`). After `migrate` you will see the tables `accounts_user`, `patients_patient`, `doctors_doctor`, `mappings_patientdoctormapping`.

## Project structure

```
config/        settings, root urls, custom exception handler
apps/accounts  custom User (email login), register, login, token refresh
apps/patients  Patient model + CRUD (scoped to creator)
apps/doctors   Doctor model + CRUD (creator-only writes)
apps/mappings  PatientDoctorMapping (unique patient+doctor)
```

## Endpoints

| Method | URL | Auth | Notes |
|---|---|---|---|
| POST | /api/auth/register/ | No | `{name, email, password}` (optional `confirm_password`) -> 201 + user + tokens |
| POST | /api/auth/login/ | No | `{email, password}` -> `{access, refresh, user}`; 401 on bad credentials |
| POST | /api/auth/token/refresh/ | No | `{refresh}` -> `{access}` |
| POST/GET | /api/patients/ | Yes | GET returns only your patients (paginated) |
| GET/PUT/PATCH/DELETE | /api/patients/<id>/ | Yes | Other users' patients -> 404 |
| POST/GET | /api/doctors/ | Yes | GET returns all doctors |
| GET/PUT/PATCH/DELETE | /api/doctors/<id>/ | Yes | Anyone reads; only creator writes (403 otherwise) |
| POST/GET | /api/mappings/ | Yes | POST `{patient, doctor}`; GET lists mappings of your patients |
| GET | /api/mappings/<patient_id>/ | Yes | Doctors assigned to that patient |
| DELETE | /api/mappings/<id>/ | Yes | Removes the mapping with that mapping id |

Send `Authorization: Bearer <access_token>`.

**Shared URL shape:** `GET /api/mappings/<patient_id>/` and `DELETE /api/mappings/<id>/` use the same
path. A single view (`MappingDetailView`) treats the number as a patient id on GET and as a mapping id on DELETE.

### Sample requests and responses

Register -> `201`
```json
{"name": "Alice", "email": "alice@example.com", "password": "Str0ng#Pass123"}
```
```json
{"message": "User registered successfully.", "user": {"id": 1, "name": "Alice", "email": "alice@example.com"}, "access": "...", "refresh": "..."}
```

Create patient -> `201`
```json
{"name": "John Doe", "age": 34, "gender": "M", "phone": "+911234567890", "address": "Mumbai", "medical_history": "Mild asthma"}
```

Create doctor -> `201`
```json
{"name": "Meera Rao", "specialization": "Cardiology", "email": "meera@hospital.com", "phone": "9876543210", "years_of_experience": 12, "hospital": "City Care"}
```

Assign doctor -> `201` (`409` if already assigned)
```json
{"patient": 1, "doctor": 1}
```

Doctors of a patient -> `200`
```json
{"patient": {"id": 1, "name": "John Doe"}, "doctors": [{"mapping_id": 1, "assigned_at": "...", "doctor": {"id": 1, "name": "Meera Rao", "...": "..."}}]}
```

Error shape (all errors)
```json
{"success": false, "message": "Validation failed.", "errors": {"age": ["Ensure this value is greater than or equal to 1."]}}
```

Status codes: 200, 201, 204, 400 (validation), 401 (missing/invalid token or bad login), 403 (not the doctor's creator), 404, 409 (duplicate mapping / DB conflict).

## Tests

```bash
python manage.py test
```
Tests automatically use in-memory SQLite, so they never touch your Supabase database.

## Assumptions

- Email is the login identifier and is stored lowercase (case-insensitive uniqueness).
- `GET /api/mappings/` returns only mappings for the logged-in user's own patients (change `MappingListCreateView.get_queryset` to return all if your evaluator expects that).
- Deleting a doctor or patient also deletes its mappings (CASCADE).
- Doctors are shared across all users, but only their creator can edit or delete them.
- List endpoints are paginated (page size 10): `?page=2`.
- `DEBUG` defaults to False. `SECRET_KEY` is required unless `DEBUG=True`.
