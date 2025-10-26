# Metropolis Parking Management System

Web-based gate control and parking management dashboard for Metropolis parking systems.

## Features

✅ **Gate Controls** - Open gates remotely at multiple sites
✅ **Auto-Monitoring** - Automatically open gates for whitelisted members
✅ **Blacklist Management** - Block specific vehicles
✅ **Token Auto-Refresh** - Automatic authentication token renewal every hour
✅ **Real-time Updates** - WebSocket-based live monitoring
✅ **Recent Visits** - View parking activity
✅ **Occupancy Tracking** - Monitor garage capacity
✅ **Emergency Controls** - Open all gates simultaneously

## Architecture

- **Backend**: Flask + Flask-SocketIO
- **Frontend**: HTML/CSS/JavaScript with Socket.IO
- **Authentication**: JWT token-based (auto-refresh)
- **Real-time**: WebSocket communication
- **Storage**: JSON file-based (members, blacklist)

## Deployment on Render.com

### Method 1: Using render.yaml (Recommended)

1. **Push to GitHub**
   ```bash
   cd render.com
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/metropolis-gate-control.git
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Set Environment Variables**
   - In Render dashboard, go to your service
   - Navigate to "Environment" tab
   - Add these variables:
     ```
     DASHBOARD_PASSWORD=your-secure-password
     METROPOLIS_EMAIL=security@555capitolmall.com
     METROPOLIS_PASSWORD=555_Security
     AUTH_KEY=(leave empty for first run)
     ```

4. **Deploy**
   - Render will automatically build and deploy
   - Wait for build to complete (~5-10 minutes)
   - Your app will be available at `https://your-app-name.onrender.com`

### Method 2: Manual Setup

1. **Create Web Service**
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: metropolis-gate-control
   - **Environment**: Python 3
   - **Build Command**:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
     ```

3. **Add Environment Variables** (same as above)

4. **Deploy**

## Local Development

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/metropolis-gate-control.git
   cd metropolis-gate-control
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome/Chromium** (for token refresh)
   - **Windows**: Download Chrome from [google.com/chrome](https://www.google.com/chrome/)
   - **macOS**: `brew install --cask google-chrome`
   - **Linux**: `sudo apt-get install google-chrome-stable chromium-chromedriver`

4. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run Application**
   ```bash
   python app.py
   ```

6. **Access Dashboard**
   - Open browser to `http://localhost:5000`
   - Login with password from `.env`

## Usage Guide

### First-Time Setup

1. **Login**
   - Use the password set in `DASHBOARD_PASSWORD` environment variable
   - Default: `metropolis123`

2. **Start Token Auto-Monitor**
   - Go to "Token Mgmt" tab
   - Click "Start Auto-Monitor"
   - This will automatically refresh your auth token every hour

3. **Add Members**
   - Go to "Members" tab
   - Enter license plates of authorized members
   - Click "Add Member"

4. **Enable Auto-Monitoring**
   - Go to "Auto-Monitor" tab
   - Click "Start Monitoring"
   - Gates will now auto-open for whitelisted members

### Daily Operation

- **Manual Gate Control**: Use "Gate Controls" tab to open gates manually
- **Monitor Activity**: Check "Recent Visits" and "Occupancy" tabs
- **Emergency**: Use "Emergency" tab to open all gates at once

### Security Notes

⚠️ **IMPORTANT SECURITY CONSIDERATIONS**:

1. **Change Default Password**: Always set a strong `DASHBOARD_PASSWORD`
2. **HTTPS Only**: Always use HTTPS in production (Render provides this automatically)
3. **Authorized Personnel**: Only share access with authorized security staff
4. **Token Security**: Never commit `AUTH_KEY` to version control
5. **Audit Logs**: All actions are logged to console (check Render logs)

## File Structure

```
render.com/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── README.md             # This file
├── .env.example          # Environment variables template
│
├── utils/                # Backend utilities
│   ├── __init__.py
│   ├── gate_control.py   # Gate API functions
│   ├── token_manager.py  # JWT token management
│   ├── monitoring.py     # Auto-monitoring logic
│   └── token_monitor.py  # Token auto-refresh
│
├── templates/            # HTML templates
│   ├── login.html        # Login page
│   └── dashboard.html    # Main dashboard
│
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Styles
│   └── js/
│       └── app.js        # Frontend JavaScript
│
└── data/                 # Data storage (auto-created)
    ├── memberships.json  # Member license plates
    └── blacklist.json    # Blacklisted plates
```

## API Endpoints

### Authentication
- `GET /` - Redirect to login or dashboard
- `POST /login` - Login with password
- `GET /logout` - Logout

### Gate Controls
- `GET /api/gates` - List all gates
- `POST /api/gate/open` - Open a specific gate
- `GET /api/occupancy/<site_id>` - Get occupancy data
- `GET /api/visits/<site_id>` - Get recent visits
- `GET /api/waiting/<site_id>` - Get cars waiting at exit

### Members & Blacklist
- `GET /api/members` - List member plates
- `POST /api/members/add` - Add member
- `POST /api/members/remove` - Remove member
- `GET /api/blacklist` - List blacklisted plates
- `POST /api/blacklist/add` - Add to blacklist
- `POST /api/blacklist/remove` - Remove from blacklist

### Token Management
- `GET /api/token/status` - Get token expiration info
- `POST /api/token/refresh` - Manually refresh token
- `GET /api/member-directory/<site_id>` - Get all members at site

### WebSocket Events
- `connect` - Client connected
- `start_monitoring` - Start auto-monitoring
- `stop_monitoring` - Stop auto-monitoring
- `start_token_monitor` - Start token auto-refresh
- `stop_token_monitor` - Stop token auto-refresh
- `monitoring_update` - Real-time monitoring updates
- `token_update` - Token status updates

## Troubleshooting

### Token Refresh Not Working

**Problem**: Selenium can't find Chrome/Chromium

**Solution**:
- On Render: The `render.yaml` includes Chrome installation
- Locally: Install Chrome browser and chromedriver

### Monitoring Not Detecting Members

**Problem**: Members added but gates not opening

**Solution**:
1. Ensure "Start Monitoring" is clicked
2. Check member license plates are exact matches (case-insensitive)
3. Check console logs for errors

### Can't Login

**Problem**: Dashboard password not working

**Solution**:
- Check `DASHBOARD_PASSWORD` environment variable in Render
- Default is `metropolis123`

### Deployment Fails on Render

**Problem**: Build fails or app crashes

**Solution**:
1. Check Render logs for specific error
2. Ensure all environment variables are set
3. Verify `requirements.txt` has correct versions
4. Check that Chrome installation succeeded in build logs

## Support & Contributing

This is an internal security tool for 555 Capitol Mall parking management.

For issues or improvements:
1. Check Render logs first
2. Verify all environment variables are set correctly
3. Test locally before deploying changes

## License

Proprietary - For authorized use only.

## Credits

Built with:
- Flask (Web framework)
- Socket.IO (Real-time communication)
- Selenium (Token automation)
- Metropolis API (Gate control)
