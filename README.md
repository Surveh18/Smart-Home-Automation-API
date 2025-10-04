# 🏠 Smart Home IoT Control System

A Django REST Framework-based smart home automation API that allows users to control IoT devices through voice commands using Google's Gemini AI. Similar to Amazon Alexa or Google Home, but with REST API access.

## 🌟 Features

- 🔐 **JWT Authentication** - Secure token-based authentication (access + refresh tokens)
- 🎮 **Device Management** - Complete CRUD operations for IoT devices
- 🎙️ **Voice Commands** - Natural language processing using Gemini AI
- 📊 **Activity Logging** - Track all device actions with timestamps
- 🔒 **User Isolation** - Each user can only access their own devices
- ✅ **Input Validation** - Real-world constraints (e.g., AC temperature 16-30°C)
- 🧪 **Unit Tests** - 23+ comprehensive test cases with 98% coverage
- 🔄 **Token Rotation** - Automatic security through token blacklisting

## 🛠️ Tech Stack

- **Backend**: Django 5.x, Django REST Framework
- **Authentication**: Simple JWT (djangorestframework-simplejwt)
- **AI Integration**: Google Gemini 2.5 Flash
- **Database**: SQLite (Development) 
- **Testing**: Django TestCase
---

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git
- Google Gemini API Key ([Get it here](https://aistudio.google.com/app/apikey))

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Surveh18/smart-home-api.git
cd smart-home-api
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables Setup

Create a `.env` file in the project root:

```bash
touch .env  # macOS/Linux
type nul > .env  # Windows
```

Add the following to `.env`:

```properties
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

**🔑 How to get Gemini API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in `.env`

### 5. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin access)
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (your secure password)

# Create normaluser from admin panel
# Username: user
# Email: user1@example.com
# Password: (your secure password)
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Server will start at: `http://127.0.0.1:8000/`

---

## 📚 API Documentation

### Base URL
```
http://127.0.0.1:8000/api/
```

### Authentication Flow

All endpoints (except login) require JWT authentication:
```
Authorization: Bearer <your_access_token>
```

---

### 🔐 Authentication Endpoints

#### 1. Login (Obtain Tokens) 
Login as normal user created in admin panel

**POST** `/api/token/`

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:** (200 OK)
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Token Lifetimes:**
- Access Token: 2 hours
- Refresh Token: 30 days

---

#### 2. Refresh Access Token

**POST** `/api/token/refresh/`

**Request Body:**
```json
{
    "refresh": "your_refresh_token"
}
```

**Response:** (200 OK)
```json
{
    "access": "new_access_token...",
    "refresh": "new_refresh_token..."
}
```

---

#### 3. Logout

**POST** `/api/logout/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "refresh": "your_refresh_token"
}
```

**Response:** (200 OK)
```json
{
    "message": "Successfully logged out",
    "note": "Your devices will remain connected until the current session expires"
}
```

---

### 🎮 Device Management Endpoints

#### 1. List All Devices

**GET** `/api/devices/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** (200 OK)
```json
[
    {
        "id": 1,
        "name": "Living Room Light",
        "device_type": "light",
        "status": "on",
        "user": "username",
        "created_at": "2025-10-04T10:30:00Z",
        "updated_at": "2025-10-04T11:00:00Z"
    },
    {
        "id": 2,
        "name": "Bedroom AC",
        "device_type": "ac",
        "status": "24",
        "user": "username",
        "created_at": "2025-10-04T10:35:00Z",
        "updated_at": "2025-10-04T10:35:00Z"
    }
]
```

---

#### 2. Create New Device

**POST** `/api/devices/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "name": "Living Room Light",
    "device_type": "light",
    "status": "off"
}
```

**Device Types:** `light`, `ac`, `thermostat`, `heater`, `fan`

**Response:** (201 Created)
```json
{
    "id": 1,
    "name": "Living Room Light",
    "device_type": "light",
    "status": "off",
    "user": "username",
    "created_at": "2025-10-04T10:30:00Z",
    "updated_at": "2025-10-04T10:30:00Z"
}
```

---

#### 3. Get Single Device

**GET** `/api/devices/{id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** (200 OK)
```json
{
    "id": 1,
    "name": "Living Room Light",
    "device_type": "light",
    "status": "on",
    "user": "username",
    "created_at": "2025-10-04T10:30:00Z",
    "updated_at": "2025-10-04T11:00:00Z"
}
```

---

#### 4. Update Device (Full Update)

**PUT** `/api/devices/{id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "name": "Living Room Smart Light",
    "device_type": "light",
    "status": "on"
}
```

**Response:** (200 OK)
```json
{
    "id": 1,
    "name": "Living Room Smart Light",
    "device_type": "light",
    "status": "on",
    ...
}
```

---

#### 5. Partial Update Device

**PATCH** `/api/devices/{id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "status": "off"
}
```

**Response:** (200 OK)
```json
{
    "id": 1,
    "name": "Living Room Smart Light",
    "device_type": "light",
    "status": "off",
    ...
}
```

---

#### 6. Delete Device

**DELETE** `/api/devices/{id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** (204 No Content)

---

### 🎮 Device Control Endpoint

#### Control Device Actions

**POST** `/api/devices/{id}/control/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (Turn On/Off):**
```json
{
    "action": "turn_on"
}
```
or
```json
{
    "action": "turn_off"
}
```

**Request Body (Set Temperature):**
```json
{
    "action": "set_temperature",
    "value": 24
}
```

**Validation Rules:**

| Device Type | Min | Max | Unit |
|-------------|-----|-----|------|
| AC | 16 | 30 | °C |
| Thermostat | 16 | 32 | °C |
| Heater | 18 | 35 | °C |
| Fan | 0 | 5 | Speed |

**Response:** (200 OK)
```json
{
    "message": "Living Room Light updated to on",
    "device": "Living Room Light",
    "new_status": "on"
}
```

**Error Response:** (400 Bad Request)
```json
{
    "error": "AC °C must be between 16 and 30"
}
```

---

### 🎙️ Voice Command Endpoint (Gemini AI)

#### Execute Natural Language Command

**POST** `/api/assistant/command/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "command": "turn on the living room light"
}
```

**Example Commands:**
- "turn on the living room light"
- "switch off bedroom fan"
- "set AC temperature to 24"
- "increase thermostat to 26 degrees"
- "turn off all lights"

**Response:** (200 OK)
```json
{
    "message": "Living Room Light updated successfully",
    "device": "Living Room Light",
    "action": "turn_on",
    "value": null,
    "new_status": "on",
    "command_understood": "turn on the living room light"
}
```

**Error Responses:**

**Device Not Found:** (404 Not Found)
```json
{
    "error": "Device 'kitchen light' not found",
    "suggestion": "Please check device name or add it first"
}
```

**Invalid Temperature:** (400 Bad Request)
```json
{
    "error": "AC °C must be between 16 and 30",
    "command": "set ac to 50 degrees",
    "device": "AC"
}
```

**Command Not Understood:** (400 Bad Request)
```json
{
    "error": "Could not understand command. Please try again."
}
```

---

### 📊 Activity Logs Endpoint

#### View All Activity Logs

**GET** `/api/logs/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** (200 OK)
```json
[
    {
        "id": 1,
        "device_id": 1,
        "action": "turn_on",
        "value": null,
        "timestamp": "2025-10-04T11:00:00Z"
    },
    {
        "id": 2,
        "device_id": 2,
        "action": "set_temperature",
        "value": "24",
        "timestamp": "2025-10-04T11:05:00Z"
    }
]
```

---

## 🧪 Running Tests

### Run All Tests
```bash
python manage.py test home.tests
```

### Run Specific Test Class
```bash
python manage.py test home.tests.AuthenticationTests
python manage.py test home.tests.DeviceCRUDTests
python manage.py test home.tests.DeviceControlTests
```

### Run with Verbose Output
```bash
python manage.py test home.tests --verbosity=2
```

### Test Coverage Report
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test home.tests

# View report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

**Test Coverage:** 98%

**Total Tests:** 23
- Authentication: 4 tests
- Device CRUD: 7 tests
- Device Control: 6 tests
- Assistant Commands: 2 tests
- Activity Logs: 2 tests
- Logout: 2 tests

---

## 📁 Project Structure

```
smart-home-api/
│
├── home/                          # Main application
│   ├── migrations/                # Database migrations
│   ├── utils/                     # Utility functions
│   │   ├── gemini.py             # Gemini AI integration
│   │   └── logger.py             # Activity logging
│   ├── models.py                 # Device and Log models
│   ├── serializers.py            # DRF serializers
│   ├── views.py                  # API views with validation
│   ├── urls.py                   # URL routing
│   └── tests.py                  # Unit tests (23 tests)
│
├── smarthome/                       # Project settings
│   ├── settings.py               # Django configuration
│   ├── urls.py                   # Root URL configuration
│   └── wsgi.py                   # WSGI configuration
│
├── .env                          # Environment variables (create this)
├── .gitignore                    # Git ignore file
├── manage.py                     # Django management script
└── requirements.txt              # Python dependencies
```

---

## 🔒 Security Features

1. **JWT Authentication**: Secure token-based auth with 2-hour access tokens
2. **Token Rotation**: Automatic refresh token rotation on refresh
3. **Token Blacklisting**: Logout invalidates refresh tokens immediately
4. **User Isolation**: Users can only access their own devices
5. **Input Validation**: Real-world constraints prevent invalid values
6. **HTTPS Ready**: Production-ready security headers

---

## 🎯 Design Decisions

### Why 30-Day Refresh Tokens?
Similar to real IoT systems like Alexa and Google Home, devices maintain persistent connections. Users don't want to re-authenticate frequently. The 30-day refresh token balances security with user experience.

### Why Optional Logout?
In real smart home ecosystems, devices stay connected even when you close the mobile app. Logout is provided for:
- Users who want explicit logout
- Security compliance requirements
- Admin ability to force logout

### Why Gemini AI?
Google's Gemini provides excellent natural language understanding for parsing voice commands into structured device actions, similar to Alexa's NLU.

---

## 🐛 Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution:** Ensure `.env` file exists in project root with valid API key

### Issue: "Token is blacklisted"
**Solution:** Login again to get fresh tokens

### Issue: "Device not found" in voice commands
**Solution:** Check device name spelling. Gemini parses case-insensitively but names must match

### Issue: Tests failing
**Solution:** 
```bash
python manage.py migrate
python manage.py test home.tests --keepdb
```
---
### Test Flow
1. **Login** → Get tokens
2. **Create Devices** → Add 3-4 devices
3. **Control Devices** → Test turn on/off
4. **Voice Commands** → Test Gemini parsing
5. **View Logs** → Check activity history
6. **Logout** → Test token blacklisting
---
