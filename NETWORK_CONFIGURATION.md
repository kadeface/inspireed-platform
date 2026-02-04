# Network Configuration Guide

## Problem: Student/Teacher WebSocket Connection Fails

### Root Cause

When teacher and student are on different machines, using `localhost` causes WebSocket connections to fail:

- **Teacher accesses:** `http://localhost:5173` → WebSocket connects to `ws://localhost:8000` ✓
- **Student accesses:** `http://192.168.1.102:5173` → WebSocket connects to `ws://192.168.1.102:8000` ✗
  - Student's browser tries to connect to backend on student's machine (192.168.1.102)
  - But backend is running on teacher's machine (localhost)
  - Connection fails!

### Solutions

#### ✅ Solution 1: Use IP Address Consistently (Recommended for LAN)

**For all users (teacher and students), access the application via the server's IP address:**

```
Teacher:  http://192.168.1.102:5173
Student:  http://192.168.1.102:5173
```

**Pros:**
- Works across all devices on the same network
- No configuration changes needed
- Simple and reliable

**Cons:**
- IP address may change if network configuration changes
- Need to ensure firewall allows connections

#### ✅ Solution 2: Use Domain Name (Recommended for Production)

Configure a domain name (e.g., via `/etc/hosts` or DNS):

```
Teacher:  http://inspireed.local:5173
Student:  http://inspireed.local:5173
```

**Setup:**
1. Add to `/etc/hosts` (on all machines) or configure DNS:
   ```
   192.168.1.102  inspireed.local
   ```

2. Update `frontend/.env.production`:
   ```bash
   VITE_API_BASE_URL=http://inspireed.local:8000/api/v1
   ```

**Pros:**
- Works across network
- Easy to remember
- Can be changed in one place if IP changes

**Cons:**
- Requires configuration on all machines
- Need admin privileges to edit `/etc/hosts`

#### ✅ Solution 3: Environment Variable Configuration

For different deployment scenarios, configure the API URL:

**Development (same machine):**
```bash
# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

**LAN deployment (different machines):**
```bash
# frontend/.env.production
VITE_API_BASE_URL=http://192.168.1.102:8000/api/v1
```

**Cloud/Production:**
```bash
# frontend/.env.production
VITE_API_BASE_URL=https://your-domain.com/api/v1
```

### Testing the Connection

#### 1. Check Backend URL

```bash
# From student's machine, test if backend is accessible:
curl http://192.168.1.102:8000/health
```

Expected output: `{"status":"ok"}`

#### 2. Check WebSocket Connection

Open browser console on student machine:

```javascript
// Should return: ws://192.168.1.102:8000
localStorage.getItem('ws_url')

// Should return a valid JWT token
localStorage.getItem('auth_token')
```

### Common Issues

#### Issue 1: CORS Errors

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:** Ensure backend CORS configuration allows the student's origin:

```python
# backend/app/main.py
origins = [
    "http://localhost:5173",
    "http://192.168.1.102:5173",
    "http://192.168.1.102:5174",  # Add all possible client addresses
]
```

#### Issue 2: Firewall Blocking Connections

**Error:** `WebSocket connection failed`, `net::ERR_CONNECTION_REFUSED`

**Solution:** Allow backend port through firewall:

```bash
# Linux/Mac
sudo ufw allow 8000/tcp

# Windows
# Add rule to Windows Firewall to allow port 8000
```

#### Issue 3: Wrong Backend URL Hardcoded

**Error:** WebSocket tries to connect to `localhost` from student machine

**Solution:** Ensure `VITE_API_BASE_URL` is NOT set or uses the correct IP:

```bash
# frontend/.env.local
# Comment out or remove:
# VITE_API_BASE_URL=http://localhost:8000/api/v1

# Let getServerBaseUrl() dynamically detect the hostname
```

### Recommended Setup for Different Scenarios

#### Scenario 1: Development (Single Machine)

```bash
# Access everything via localhost
Teacher: http://localhost:5173
Student: http://localhost:5173 (different browser or incognito)
Backend: http://localhost:8000
```

#### Scenario 2: LAN Testing (Multiple Machines)

```bash
# Use server's IP address
Teacher: http://192.168.1.102:5173
Student: http://192.168.1.102:5173
Backend: Runs on machine with IP 192.168.1.102:8000
```

#### Scenario 3: Production Deployment

```bash
# Use domain name with SSL
Teacher: https://inspireed.example.com
Student: https://inspireed.example.com
Backend: https://api.inspireed.example.com (or same domain with reverse proxy)
```

### Verification Checklist

- [ ] Backend is accessible from student's machine: `curl http://SERVER_IP:8000/health`
- [ ] All users access via same protocol (all http:// or all https://)
- [ ] All users access via same hostname (all IP, all domain, etc.)
- [ ] Firewall allows backend port (8000)
- [ ] CORS configuration allows student origin
- [ ] WebSocket URL in browser console shows correct server address
- [ ] No hardcoded `localhost` in environment variables for multi-machine setup
