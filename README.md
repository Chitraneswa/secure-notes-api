# secure-notes-api
📝 Secure Notes API

A secure, JWT-authenticated Notes Management API built with Flask, MongoDB, and Docker.
Designed with modular architecture, interactive API documentation, and best security practices for authentication and data storage.

🚀 Features

🔐 JWT Authentication — Protects all sensitive endpoints.

🛡 Secure Password Storage — Uses bcrypt hashing.

📜 CRUD for Notes — Create, read, update, delete personal notes.

🔍 Search Functionality — Filter notes by title or content.

📄 Interactive API Docs — Built-in Swagger UI via Flasgger.

🐳 Dockerized — Easy deployment in any environment.

🌱 Environment Configurable — All secrets stored in .env.

🛠 Tech Stack

Backend: Python 3.11, Flask

Database: MongoDB Atlas (PyMongo)

Auth: JWT (PyJWT), bcrypt

Docs: Swagger (Flasgger)

Deployment: Docker

Config: python-dotenv

📂 Project Structure

📦 notes-app/
│── app.py # Main app entry point & routes
│── auth.py # Auth routes: signup, login
│── db.py # Centralized MongoDB connection
│── config.py # Loads environment variables
│── utilities.py # Helper functions & JWT decorator
│── requirements.txt # Python dependencies
│── DockerFile # Docker build instructions
│── .gitignore # Ignored files for Git
│── README.md # Documentation
│── .env # Environment variables (ignored in Git)

⚙️ Installation & Setup

1️⃣ Clone the Repository
git clone https://github.com/yourusername/secure-notes-api.git
cd secure-notes-api

2️⃣ Create .env File
SECRET_KEY=your_secret_key
MONGO_URI=your_mongo_uri

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Locally
python app.py


API will be available at:

http://localhost:5000

🐳 Run with Docker
docker build -t secure-notes-api .
docker run -p 5000:5000 secure-notes-api

📖 API Documentation

Once the server is running, open:

http://localhost:5000/apidocs


Here you can test all endpoints interactively.

## 🔌 API Endpoints

### **Authentication**
| Method | Endpoint   | Description            | Auth Required | Request Body |
|--------|-----------|------------------------|---------------|--------------|
| POST   | `/signup` | Register new user      | ❌ No         | `{ "username": "string", "password": "string" }` |
| POST   | `/login`  | Login and get JWT token| ❌ No         | `{ "username": "string", "password": "string" }` |

### **Notes**
| Method | Endpoint       | Description                              | Auth Required | Request Body |
|--------|---------------|------------------------------------------|---------------|--------------|
| GET    | `/notes`      | Get all notes (optional `?search=` param) | ✅ Yes        | N/A |
| POST   | `/addNote`    | Create a new note                         | ✅ Yes        | `{ "title": "string", "text": "string", "freeze": "true/false" }` |
| PUT    | `/updateNote` | Update an existing note                   | ✅ Yes        | `{ "id": "string", "title": "string", "text": "string", "freeze": "true/false" }` |
| DELETE | `/deleteNote` | Delete a note by ID                       | ✅ Yes        | `{ "id": "string" }` |


🔐 Authentication Flow

Sign Up → /signup (creates user, returns token)

Login → /login (returns token)

Use Token → Include Authorization: Bearer <token> header for protected endpoints.

📜 License

MIT License — feel free to fork and modify.
