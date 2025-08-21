const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static('public'));
app.set('view engine', 'html');

// In-memory storage for users and sessions
const users = {};
const sessions = {};

// Helper function to generate session ID
function generateSessionId() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

// Helper function to read HTML files
function readHTMLFile(filename) {
    try {
        return fs.readFileSync(path.join(__dirname, 'templates', filename), 'utf8');
    } catch (error) {
        return '<h1>Template not found</h1>';
    }
}

// Stroke prediction algorithm
function predictStroke(data) {
    let riskScore = 0;
    
    // Age factor (higher age = higher risk)
    const age = parseInt(data.age) || 0;
    if (age > 65) riskScore += 30;
    else if (age > 50) riskScore += 20;
    else if (age > 35) riskScore += 10;
    
    // Gender factor
    if (data.gender === 'Male') riskScore += 5;
    
    // Medical conditions
    if (data.hypertension === '1') riskScore += 25;
    if (data.heart_disease === '1') riskScore += 25;
    
    // Glucose level
    const glucose = parseFloat(data.avg_glucose_level) || 0;
    if (glucose > 200) riskScore += 20;
    else if (glucose > 140) riskScore += 15;
    else if (glucose > 100) riskScore += 5;
    
    // BMI
    const bmi = parseFloat(data.bmi) || 0;
    if (bmi > 30) riskScore += 15;
    else if (bmi > 25) riskScore += 8;
    
    // Smoking status
    if (data.smoking_status === 'smokes') riskScore += 20;
    else if (data.smoking_status === 'formerly smoked') riskScore += 10;
    
    // Work type stress factor
    if (data.work_type === 'Private') riskScore += 5;
    
    // Marriage status (married people tend to have better health outcomes)
    if (data.ever_married === 'No') riskScore += 5;
    
    // Calculate probability (cap at 95%)
    const probability = Math.min(riskScore, 95);
    
    return {
        risk_level: probability > 60 ? 'High Risk' : probability > 30 ? 'Moderate Risk' : 'Low Risk',
        probability: probability,
        recommendation: probability > 60 ? 
            'Please consult with a healthcare professional immediately for a comprehensive evaluation.' :
            probability > 30 ?
            'Consider lifestyle modifications and regular health check-ups.' :
            'Maintain current healthy lifestyle and regular medical check-ups.'
    };
}

// Routes
app.get('/', (req, res) => {
    const sessionId = req.headers.cookie?.split('session_id=')[1]?.split(';')[0];
    if (sessionId && sessions[sessionId]) {
        res.redirect('/home');
    } else {
        const html = readHTMLFile('index.html');
        res.send(html);
    }
});

app.get('/register', (req, res) => {
    const html = readHTMLFile('register.html');
    res.send(html);
});

app.post('/register', (req, res) => {
    const { username, password } = req.body;
    
    if (users[username]) {
        res.send('<script>alert("Username already exists!"); window.location.href="/register";</script>');
        return;
    }
    
    users[username] = { password };
    res.send('<script>alert("Registration successful!"); window.location.href="/";</script>');
});

app.get('/login', (req, res) => {
    const html = readHTMLFile('login.html');
    res.send(html);
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    
    if (users[username] && users[username].password === password) {
        const sessionId = generateSessionId();
        sessions[sessionId] = { username };
        res.setHeader('Set-Cookie', `session_id=${sessionId}; Path=/`);
        res.redirect('/home');
    } else {
        res.send('<script>alert("Invalid credentials!"); window.location.href="/login";</script>');
    }
});

app.get('/home', (req, res) => {
    const sessionId = req.headers.cookie?.split('session_id=')[1]?.split(';')[0];
    if (!sessionId || !sessions[sessionId]) {
        res.redirect('/');
        return;
    }
    
    const html = readHTMLFile('home.html');
    res.send(html);
});

app.post('/predict', (req, res) => {
    const sessionId = req.headers.cookie?.split('session_id=')[1]?.split(';')[0];
    if (!sessionId || !sessions[sessionId]) {
        res.redirect('/');
        return;
    }
    
    const prediction = predictStroke(req.body);
    
    const resultHTML = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stroke Prediction Result</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 600px;
                width: 100%;
            }
            .result-header {
                color: #333;
                margin-bottom: 30px;
            }
            .risk-level {
                font-size: 2em;
                font-weight: bold;
                margin: 20px 0;
                padding: 20px;
                border-radius: 10px;
            }
            .high-risk { background: #ffebee; color: #c62828; }
            .moderate-risk { background: #fff3e0; color: #ef6c00; }
            .low-risk { background: #e8f5e8; color: #2e7d32; }
            .probability {
                font-size: 1.5em;
                margin: 20px 0;
                color: #555;
            }
            .recommendation {
                background: #f5f5f5;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                color: #333;
                line-height: 1.6;
            }
            .buttons {
                margin-top: 30px;
            }
            .btn {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin: 0 10px;
                font-size: 16px;
                transition: transform 0.2s;
            }
            .btn:hover {
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="result-header">🧠 Stroke Risk Assessment Result</h1>
            
            <div class="risk-level ${prediction.risk_level.toLowerCase().replace(' ', '-')}">
                ${prediction.risk_level}
            </div>
            
            <div class="probability">
                Risk Probability: ${prediction.probability}%
            </div>
            
            <div class="recommendation">
                <strong>Recommendation:</strong><br>
                ${prediction.recommendation}
            </div>
            
            <div class="buttons">
                <a href="/home" class="btn">New Prediction</a>
                <a href="/logout" class="btn">Logout</a>
            </div>
            
            <p style="margin-top: 30px; color: #666; font-size: 14px;">
                <em>Disclaimer: This prediction is for educational purposes only and should not replace professional medical advice.</em>
            </p>
        </div>
    </body>
    </html>
    `;
    
    res.send(resultHTML);
});

app.get('/logout', (req, res) => {
    const sessionId = req.headers.cookie?.split('session_id=')[1]?.split(';')[0];
    if (sessionId) {
        delete sessions[sessionId];
    }
    res.setHeader('Set-Cookie', 'session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT');
    res.redirect('/');
});

app.listen(PORT, () => {
    console.log(`Brain Stroke Prediction App running on http://localhost:${PORT}`);
});