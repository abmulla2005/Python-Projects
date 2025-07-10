# 🖼️ Tornado Image Uploader

A simple Tornado-based web application to upload, view, and delete image files. Also provides an API to access image metadata.

## 🚀 Features

- 📤 Upload image files (JPG, PNG, GIF, BMP, WebP, etc.)
- 🗂️ View uploaded images in a responsive gallery
- ❌ Delete uploaded images
- 📊 Get JSON metadata of all uploaded images via `/image-data` API
- 🛡️ Filename sanitization and file size restriction (max 5MB)

---

## 📁 Project Structure

.
├── main.py # Tornado server with upload/delete/image API
├── upload/ # Uploaded images (auto-created)
├── templates/
│ └── index.html # Gallery and upload form
├── README.md # Project documentation

yaml
Copy
Edit

---

## ⚙️ How to Run

### 1. 🔧 Install dependencies

```bash
pip install tornado
2. ▶️ Start the server
bash
Copy
Edit
python main.py
The server will run at:
📍 http://localhost:8080

📷 API Endpoint
Get image metadata (JSON)
h
Copy
Edit
GET /image-data
Example response:

json
Copy
Edit
[
  {
    "filename": "abcd1234_image.jpg",
    "upload_date": "2025-07-10",
    "upload_time": "14:30:45",
    "file_size": 123456,
    "file_path": "/img/abcd1234_image.jpg"
  }
]
🔐 Security Features
Filenames are sanitized and made unique using UUID

Only image files are accepted

Max upload file size: 5MB

Strict delete validation to prevent path traversal

🗑️ Delete Image
Submit a POST request to /delete with a filename field matching the uploaded filename.

📌 Notes
Uploaded files are saved in the upload/ folder.

The upload folder is automatically created if not found.

Template files are stored in templates/index.html.

🧑‍💻 Author
Made with ❤️ using Tornado.

🏷️ License
MIT License – free to use, modify, and distribute.

yaml
Copy
Edit

---

### ✅ Save it as:

```bash
README.md
