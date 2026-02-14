# Start both frontend and backend servers

Write-Host "🚀 Starting VidyaSetu AI..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    python --version | Out-Null
    Write-Host "✅ Python found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check if Node is installed
try {
    node --version | Out-Null
    Write-Host "✅ Node.js found" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow

# Install frontend dependencies
if (!(Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..."
    npm install
}

# Install backend dependencies  
if (!(Test-Path "backend/venv")) {
    Write-Host "Installing backend dependencies..."
    cd backend
    pip install -r requirements.txt
    cd ..
}

Write-Host ""
Write-Host "🎬 Starting servers..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend will run on: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend will run on: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host ""

# Start both servers in separate processes
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py" -PassThru
Start-Sleep -Seconds 3
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -PassThru

Write-Host "✅ Both servers started!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend PID: $($backend.Id)" -ForegroundColor Gray
Write-Host "Frontend PID: $($frontend.Id)" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop, close the PowerShell windows or run: Stop-Process -Id $($backend.Id),$($frontend.Id)" -ForegroundColor Gray
