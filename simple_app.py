#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import html

# Simple web server to replace Flask
class StrokePredictor:
    def __init__(self):
        self.users_file = 'users.json'
        self.sessions = {}
        
    def load_users(self):
        if not os.path.exists(self.users_file):
            return {}
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_users(self, users):
        with open(self.users_file, 'w') as f:
            json.dump(users, f)
    
    def simple_stroke_prediction(self, features):
        """Simple rule-based stroke prediction without ML libraries"""
        age, glucose, bmi, gender, hypertension, heart_disease, married, work, residence, smoking = features
        
        risk_score = 0
        
        # Age factor
        if age > 65:
            risk_score += 3
        elif age > 45:
            risk_score += 2
        elif age > 30:
            risk_score += 1
            
        # Glucose level
        if glucose > 200:
            risk_score += 3
        elif glucose > 140:
            risk_score += 2
        elif glucose > 100:
            risk_score += 1
            
        # BMI
        if bmi > 30:
            risk_score += 2
        elif bmi > 25:
            risk_score += 1
            
        # Medical conditions
        if hypertension:
            risk_score += 2
        if heart_disease:
            risk_score += 3
            
        # Smoking
        if smoking == 3:  # Current smoker
            risk_score += 2
        elif smoking == 1:  # Former smoker
            risk_score += 1
            
        # Return prediction based on risk score
        return 1 if risk_score >= 5 else 0

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.predictor = StrokePredictor()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/home':
            self.serve_home()
        elif path == '/login':
            self.serve_login()
        elif path == '/register':
            self.serve_register()
        elif path == '/index':
            self.serve_index()
        elif path == '/logout':
            self.handle_logout()
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)
        
        # Convert form data to simple dict
        data = {}
        for key, value in form_data.items():
            data[key] = value[0] if value else ''
        
        if path == '/login':
            self.handle_login(data)
        elif path == '/register':
            self.handle_register(data)
        elif path == '/predict':
            self.handle_predict(data)
        else:
            self.send_error(404)
    
    def serve_home(self):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Brain Stroke Prediction</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
                h1 { color: #333; text-align: center; margin-bottom: 30px; }
                .btn { display: inline-block; padding: 12px 24px; margin: 10px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; transition: background 0.3s; }
                .btn:hover { background: #5a67d8; }
                .description { text-align: center; margin: 20px 0; color: #666; line-height: 1.6; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧠 Brain Stroke Prediction System</h1>
                <div class="description">
                    <p>Welcome to our AI-powered brain stroke prediction system. This application uses advanced algorithms to assess stroke risk based on various health factors.</p>
                    <p>Please login or register to access the prediction system.</p>
                </div>
                <div style="text-align: center;">
                    <a href="/login" class="btn">Login</a>
                    <a href="/register" class="btn">Register</a>
                </div>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_login(self, error=None):
        error_msg = f'<div style="color: red; margin: 10px 0;">{error}</div>' if error else ''
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - Brain Stroke Prediction</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .container {{ max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
                h2 {{ text-align: center; color: #333; margin-bottom: 30px; }}
                .form-group {{ margin: 20px 0; }}
                label {{ display: block; margin-bottom: 5px; color: #555; }}
                input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
                .btn {{ width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
                .btn:hover {{ background: #5a67d8; }}
                .link {{ text-align: center; margin-top: 20px; }}
                .link a {{ color: #667eea; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Login</h2>
                {error_msg}
                <form method="post" action="/login">
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn">Login</button>
                </form>
                <div class="link">
                    <a href="/register">Don't have an account? Register here</a>
                </div>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_register(self, error=None):
        error_msg = f'<div style="color: red; margin: 10px 0;">{error}</div>' if error else ''
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Register - Brain Stroke Prediction</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .container {{ max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
                h2 {{ text-align: center; color: #333; margin-bottom: 30px; }}
                .form-group {{ margin: 20px 0; }}
                label {{ display: block; margin-bottom: 5px; color: #555; }}
                input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
                .btn {{ width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
                .btn:hover {{ background: #5a67d8; }}
                .link {{ text-align: center; margin-top: 20px; }}
                .link a {{ color: #667eea; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Register</h2>
                {error_msg}
                <form method="post" action="/register">
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn">Register</button>
                </form>
                <div class="link">
                    <a href="/login">Already have an account? Login here</a>
                </div>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_index(self, prediction=None):
        prediction_msg = f'<div style="background: {"#d4edda" if "does not have" in prediction else "#f8d7da"}; color: {"#155724" if "does not have" in prediction else "#721c24"}; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center; font-weight: bold;">{prediction}</div>' if prediction else ''
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Stroke Prediction - Brain Stroke Prediction</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
                h1 {{ text-align: center; color: #333; margin-bottom: 30px; }}
                .form-group {{ margin: 15px 0; }}
                label {{ display: block; margin-bottom: 5px; color: #555; font-weight: bold; }}
                input, select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
                .btn {{ width: 100%; padding: 15px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 20px; }}
                .btn:hover {{ background: #5a67d8; }}
                .logout {{ float: right; background: #dc3545; padding: 8px 16px; color: white; text-decoration: none; border-radius: 3px; }}
                .logout:hover {{ background: #c82333; }}
                .row {{ display: flex; gap: 20px; }}
                .col {{ flex: 1; }}
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/logout" class="logout">Logout</a>
                <h1>🧠 Brain Stroke Prediction</h1>
                {prediction_msg}
                <form method="post" action="/predict">
                    <div class="row">
                        <div class="col">
                            <div class="form-group">
                                <label>Gender:</label>
                                <select name="gender" required>
                                    <option value="">Select Gender</option>
                                    <option value="0">Female</option>
                                    <option value="1">Male</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Age:</label>
                                <input type="number" name="age" min="1" max="120" required>
                            </div>
                            <div class="form-group">
                                <label>Hypertension:</label>
                                <select name="hypertension" required>
                                    <option value="">Select</option>
                                    <option value="0">No</option>
                                    <option value="1">Yes</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Heart Disease:</label>
                                <select name="disease" required>
                                    <option value="">Select</option>
                                    <option value="0">No</option>
                                    <option value="1">Yes</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Ever Married:</label>
                                <select name="married" required>
                                    <option value="">Select</option>
                                    <option value="0">No</option>
                                    <option value="1">Yes</option>
                                </select>
                            </div>
                        </div>
                        <div class="col">
                            <div class="form-group">
                                <label>Work Type:</label>
                                <select name="work" required>
                                    <option value="">Select Work Type</option>
                                    <option value="1">Never Worked</option>
                                    <option value="2">Private</option>
                                    <option value="3">Self-employed</option>
                                    <option value="4">Children</option>
                                    <option value="0">Government Job</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Residence Type:</label>
                                <select name="residence" required>
                                    <option value="">Select</option>
                                    <option value="0">Rural</option>
                                    <option value="1">Urban</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Average Glucose Level:</label>
                                <input type="number" name="avg_glucose_level" step="0.01" min="50" max="400" required>
                            </div>
                            <div class="form-group">
                                <label>BMI:</label>
                                <input type="number" name="bmi" step="0.1" min="10" max="60" required>
                            </div>
                            <div class="form-group">
                                <label>Smoking Status:</label>
                                <select name="smoking" required>
                                    <option value="">Select</option>
                                    <option value="1">Formerly Smoked</option>
                                    <option value="2">Never Smoked</option>
                                    <option value="3">Smokes</option>
                                    <option value="0">Unknown</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <button type="submit" class="btn">Predict Stroke Risk</button>
                </form>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def handle_login(self, data):
        username = data.get('username', '')
        password = data.get('password', '')
        users = self.predictor.load_users()
        
        if username in users and users[username]['password'] == password:
            self.sessions[username] = True
            self.send_response(302)
            self.send_header('Location', '/index')
            self.end_headers()
        else:
            self.serve_login('Invalid credentials. Please try again.')
    
    def handle_register(self, data):
        username = data.get('username', '')
        password = data.get('password', '')
        users = self.predictor.load_users()
        
        if username not in users:
            users[username] = {'password': password}
            self.predictor.save_users(users)
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
        else:
            self.serve_register('Username already exists.')
    
    def handle_logout(self):
        self.send_response(302)
        self.send_header('Location', '/login')
        self.end_headers()
    
    def handle_predict(self, data):
        try:
            # Extract features
            age = int(data.get('age', 0))
            glucose = float(data.get('avg_glucose_level', 0))
            bmi = float(data.get('bmi', 0))
            gender = int(data.get('gender', 0))
            hypertension = int(data.get('hypertension', 0))
            heart_disease = int(data.get('disease', 0))
            married = int(data.get('married', 0))
            work = int(data.get('work', 0))
            residence = int(data.get('residence', 0))
            smoking = int(data.get('smoking', 0))
            
            features = [age, glucose, bmi, gender, hypertension, heart_disease, married, work, residence, smoking]
            prediction = self.predictor.simple_stroke_prediction(features)
            
            if prediction == 1:
                prediction_text = 'Patient has stroke risk'
            else:
                prediction_text = 'Congratulations, patient does not have stroke risk'
            
            self.serve_index(prediction_text)
        except Exception as e:
            self.serve_index(f'Error in prediction: {str(e)}')

def run_server():
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on http://localhost:5000")
    print("Access the application at: http://localhost:5000")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()