import tornado.web
import tornado.ioloop
import os
import re
import uuid
import datetime
from tornado.escape import json_encode

class UploadHandler(tornado.web.RequestHandler):
    def get(self):
        # Create upload directory if not exists
        upload_path = os.path.abspath("upload")
        os.makedirs(upload_path, exist_ok=True)
        
        # Get list of image files with metadata
        images = []
        for filename in os.listdir(upload_path):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")):
                file_path = os.path.join(upload_path, filename)
                stat = os.stat(file_path)
                created_time = datetime.datetime.fromtimestamp(stat.st_ctime)
                images.append({
                    'name': filename,
                    'date': created_time.strftime('%Y-%m-%d'),
                    'time': created_time.strftime('%H:%M:%S'),
                    'size': stat.st_size
                })
        
        # Render template with images
        self.render("index.html", images=images)

    def post(self):
        # Handle file upload
        if "fileImage" in self.request.files:
            file = self.request.files["fileImage"][0]
            original_name = file["filename"]
            body = file["body"]
            
            # Security enhancements
            if len(body) > 5 * 1024 * 1024:  # 5MB limit
                self.write("File too large (max 5MB)")
                return
                
            # Clean filename and make unique
            clean_name = re.sub(r'[^\w\.-]', '', original_name)
            unique_name = f"{uuid.uuid4().hex}_{clean_name}"
            
            # Create upload directory if not exists
            upload_path = os.path.abspath("upload")
            os.makedirs(upload_path, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_path, unique_name)
            with open(file_path, "wb") as f:
                f.write(body)
            
            self.redirect("/")
        else:
            self.write("No file uploaded")

class DeleteHandler(tornado.web.RequestHandler):
    def post(self):
        filename = self.get_body_argument("filename")
        
        # Validate filename
        if not re.match(r'^[a-f0-9]{32}_[\w\.-]+$', filename):  # More strict validation
            self.set_status(400)
            self.write("Invalid filename format")
            return
            
        upload_path = os.path.abspath("upload")
        file_path = os.path.join(upload_path, filename)
        
        # Additional security check
        if not os.path.exists(upload_path):
            self.set_status(404)
            self.write("Upload directory not found")
            return
            
        # Check if file exists and delete
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                self.redirect("/")
            except Exception as e:
                self.set_status(500)
                self.write(f"Error deleting file: {str(e)}")
        else:
            self.set_status(404)
            self.write("File not found")

class ImageDataHandler(tornado.web.RequestHandler):
    def get(self):
        upload_path = os.path.abspath("upload")
        os.makedirs(upload_path, exist_ok=True)
        
        image_data = []
        for filename in os.listdir(upload_path):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")):
                file_path = os.path.join(upload_path, filename)
                stat = os.stat(file_path)
                created_time = datetime.datetime.fromtimestamp(stat.st_ctime)
                
                image_data.append({
                    'filename': filename,
                    'upload_date': created_time.strftime('%Y-%m-%d'),
                    'upload_time': created_time.strftime('%H:%M:%S'),
                    'file_size': stat.st_size,
                    'file_path': f"/img/{filename}"
                })
        
        self.set_header("Content-Type", "application/json")
        self.write(json_encode(image_data))

def make_app():
    return tornado.web.Application([
        (r"/", UploadHandler),
        (r"/img/(.*)", tornado.web.StaticFileHandler, {"path": "upload"}),
        (r"/delete", DeleteHandler),
        (r"/image-data", ImageDataHandler),
    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    print("🚀 Server running at http://localhost:8080")
    print("📸 Image metadata available at http://localhost:8080/image-data")
    tornado.ioloop.IOLoop.current().start()