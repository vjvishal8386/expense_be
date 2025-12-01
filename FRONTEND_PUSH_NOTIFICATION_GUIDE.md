# Frontend Push Notification Integration Guide
## Step-by-Step Implementation

This guide will help you integrate Firebase Cloud Messaging (FCM) push notifications into your frontend application (React/Next.js/Vue/etc.).

---

## Prerequisites

- Firebase project created
- Firebase Web App configured
- Backend API running with notification endpoints
- User authentication working

---

## Step 1: Install Firebase SDK

### For React/Next.js

```bash
npm install firebase
# or
yarn add firebase
```

### For Vue.js

```bash
npm install firebase
```

---

## Step 2: Get Firebase Configuration

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click the gear icon ⚙️ → Project Settings
4. Scroll down to "Your apps" section
5. Click on Web app (or create one)
6. Copy the Firebase configuration object

It will look like:
```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

---

## Step 3: Create Firebase Service File

Create a file to initialize Firebase: `src/services/firebase.js` (or `src/lib/firebase.js`)

```javascript
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Cloud Messaging and get a reference to the service
let messaging = null;

if (typeof window !== 'undefined') {
  messaging = getMessaging(app);
}

export { messaging, app };
```

---

## Step 4: Get VAPID Key

1. In Firebase Console → Project Settings
2. Go to "Cloud Messaging" tab
3. Scroll to "Web Push certificates"
4. Click "Generate key pair" (if not already generated)
5. Copy the **VAPID key** (it looks like: `BKx...`)

**Important**: Save this key - you'll need it in the next step.

---

## Step 5: Create Notification Service

Create `src/services/notificationService.js`:

```javascript
import { messaging } from './firebase';
import { getToken, onMessage } from 'firebase/messaging';

// Your VAPID key from Firebase Console
const VAPID_KEY = 'YOUR_VAPID_KEY_HERE';

// Your backend API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Request notification permission from user
 */
export async function requestNotificationPermission() {
  try {
    const permission = await Notification.requestPermission();
    
    if (permission === 'granted') {
      console.log('Notification permission granted');
      return true;
    } else {
      console.log('Notification permission denied');
      return false;
    }
  } catch (error) {
    console.error('Error requesting notification permission:', error);
    return false;
  }
}

/**
 * Get FCM token for current device
 */
export async function getFCMToken() {
  try {
    if (!messaging) {
      console.error('Messaging not initialized');
      return null;
    }

    const token = await getToken(messaging, {
      vapidKey: VAPID_KEY
    });

    if (token) {
      console.log('FCM Token:', token);
      return token;
    } else {
      console.log('No registration token available');
      return null;
    }
  } catch (error) {
    console.error('An error occurred while retrieving token:', error);
    return null;
  }
}

/**
 * Register device token with backend
 */
export async function registerDeviceToken(token, authToken) {
  try {
    const response = await fetch(`${API_BASE_URL}/notifications/register-device`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        token: token,
        platform: 'web',
        device_info: {
          userAgent: navigator.userAgent,
          language: navigator.language,
          platform: navigator.platform
        }
      })
    });

    if (!response.ok) {
      throw new Error('Failed to register device token');
    }

    const data = await response.json();
    console.log('Device token registered:', data);
    return data;
  } catch (error) {
    console.error('Error registering device token:', error);
    throw error;
  }
}

/**
 * Unregister device token
 */
export async function unregisterDeviceToken(tokenId, authToken) {
  try {
    const response = await fetch(`${API_BASE_URL}/notifications/device/${tokenId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to unregister device token');
    }

    console.log('Device token unregistered');
  } catch (error) {
    console.error('Error unregistering device token:', error);
    throw error;
  }
}

/**
 * Get all registered device tokens for current user
 */
export async function getMyDeviceTokens(authToken) {
  try {
    const response = await fetch(`${API_BASE_URL}/notifications/devices`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to get device tokens');
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting device tokens:', error);
    throw error;
  }
}

/**
 * Setup listener for foreground messages (when app is open)
 */
export function setupForegroundMessageListener(callback) {
  if (!messaging) {
    console.error('Messaging not initialized');
    return;
  }

  onMessage(messaging, (payload) => {
    console.log('Message received in foreground:', payload);
    
    // Show browser notification
    if (payload.notification) {
      showBrowserNotification(
        payload.notification.title,
        payload.notification.body,
        payload.data
      );
    }
    
    // Call custom callback if provided
    if (callback) {
      callback(payload);
    }
  });
}

/**
 * Show browser notification
 */
function showBrowserNotification(title, body, data = {}) {
  if ('Notification' in window && Notification.permission === 'granted') {
    const notification = new Notification(title, {
      body: body,
      icon: '/icon-192x192.png', // Your app icon
      badge: '/badge-72x72.png',
      tag: data.expense_id || 'expense-notification',
      data: data
    });

    // Handle notification click
    notification.onclick = (event) => {
      event.preventDefault();
      window.focus();
      
      // Navigate to expense detail if expense_id is present
      if (data.friend_id) {
        window.location.href = `/expenses/${data.friend_id}`;
      }
      
      notification.close();
    };
  }
}

/**
 * Initialize push notifications (call this when user logs in)
 */
export async function initializePushNotifications(authToken) {
  try {
    // 1. Request permission
    const hasPermission = await requestNotificationPermission();
    if (!hasPermission) {
      console.log('User denied notification permission');
      return false;
    }

    // 2. Get FCM token
    const fcmToken = await getFCMToken();
    if (!fcmToken) {
      console.log('Failed to get FCM token');
      return false;
    }

    // 3. Register token with backend
    await registerDeviceToken(fcmToken, authToken);
    
    // 4. Setup foreground message listener
    setupForegroundMessageListener((payload) => {
      // Handle notification data
      console.log('Notification received:', payload);
      // You can update your app state here, show toast, etc.
    });

    console.log('Push notifications initialized successfully');
    return true;
  } catch (error) {
    console.error('Error initializing push notifications:', error);
    return false;
  }
}
```

---

## Step 6: Create Service Worker for Background Notifications

Create `public/firebase-messaging-sw.js`:

```javascript
// Import Firebase scripts
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Your Firebase config (same as in your app)
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Retrieve an instance of Firebase Messaging
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message:', payload);

  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    tag: payload.data.expense_id || 'expense-notification',
    data: payload.data
  };

  return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  console.log('[firebase-messaging-sw.js] Notification click received.');

  event.notification.close();

  // Navigate to expense detail page
  if (event.notification.data && event.notification.data.friend_id) {
    event.waitUntil(
      clients.openWindow(`/expenses/${event.notification.data.friend_id}`)
    );
  }
});
```

**Note**: Make sure this file is in the `public` folder so it's accessible at `/firebase-messaging-sw.js`

---

## Step 7: Register Service Worker in Your App

Update your `src/services/firebase.js`:

```javascript
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage, isSupported } from 'firebase/messaging';

const firebaseConfig = {
  // ... your config
};

const app = initializeApp(firebaseConfig);

let messaging = null;

if (typeof window !== 'undefined') {
  // Check if messaging is supported
  isSupported().then((supported) => {
    if (supported) {
      messaging = getMessaging(app);
      
      // Register service worker
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/firebase-messaging-sw.js')
          .then((registration) => {
            console.log('Service Worker registered:', registration);
          })
          .catch((error) => {
            console.error('Service Worker registration failed:', error);
          });
      }
    }
  });
}

export { messaging, app };
```

---

## Step 8: Integrate in Your React Component

### Option A: Using a Hook (Recommended)

Create `src/hooks/usePushNotifications.js`:

```javascript
import { useState, useEffect } from 'react';
import {
  initializePushNotifications,
  getMyDeviceTokens,
  unregisterDeviceToken
} from '../services/notificationService';

export function usePushNotifications(authToken) {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deviceTokens, setDeviceTokens] = useState([]);

  useEffect(() => {
    if (authToken && !isInitialized) {
      initializeNotifications();
    }
  }, [authToken, isInitialized]);

  const initializeNotifications = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const success = await initializePushNotifications(authToken);
      if (success) {
        setIsInitialized(true);
        await loadDeviceTokens();
      }
    } catch (err) {
      setError(err.message);
      console.error('Failed to initialize push notifications:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadDeviceTokens = async () => {
    try {
      const tokens = await getMyDeviceTokens(authToken);
      setDeviceTokens(tokens);
    } catch (err) {
      console.error('Failed to load device tokens:', err);
    }
  };

  const removeDeviceToken = async (tokenId) => {
    try {
      await unregisterDeviceToken(tokenId, authToken);
      await loadDeviceTokens();
    } catch (err) {
      console.error('Failed to remove device token:', err);
    }
  };

  return {
    isInitialized,
    isLoading,
    error,
    deviceTokens,
    removeDeviceToken,
    reloadTokens: loadDeviceTokens
  };
}
```

### Use in Your App Component

```javascript
import React, { useEffect } from 'react';
import { usePushNotifications } from './hooks/usePushNotifications';
import { setupForegroundMessageListener } from './services/notificationService';

function App() {
  const authToken = localStorage.getItem('authToken'); // Get from your auth context
  const { isInitialized, isLoading, error } = usePushNotifications(authToken);

  useEffect(() => {
    if (isInitialized) {
      // Setup listener for foreground notifications
      setupForegroundMessageListener((payload) => {
        // Handle notification
        console.log('New expense notification:', payload);
        
        // Show toast notification
        // toast.success(`${payload.notification.title}: ${payload.notification.body}`);
        
        // Update expenses list if needed
        // refreshExpenses();
      });
    }
  }, [isInitialized]);

  if (isLoading) {
    return <div>Initializing notifications...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="App">
      {/* Your app content */}
    </div>
  );
}

export default App;
```

### Option B: Simple Integration in Login/Auth Component

```javascript
import { useEffect } from 'react';
import { initializePushNotifications } from '../services/notificationService';

function LoginComponent() {
  const handleLogin = async (authToken) => {
    // After successful login
    localStorage.setItem('authToken', authToken);
    
    // Initialize push notifications
    await initializePushNotifications(authToken);
  };

  return (
    // Your login form
  );
}
```

---

## Step 9: Handle Notification Click Navigation

Update your router to handle notification deep links:

```javascript
// In your router file (React Router example)
import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function NotificationHandler() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Check if we came from a notification
    const params = new URLSearchParams(location.search);
    const expenseId = params.get('expense_id');
    const friendId = params.get('friend_id');

    if (expenseId || friendId) {
      // Navigate to expense detail
      navigate(`/expenses/${friendId}`);
    }
  }, [location, navigate]);

  return null;
}
```

---

## Step 10: Add Notification Settings UI (Optional)

Create a component to manage notification preferences:

```javascript
import React, { useState, useEffect } from 'react';
import { getMyDeviceTokens, unregisterDeviceToken } from '../services/notificationService';

function NotificationSettings({ authToken }) {
  const [deviceTokens, setDeviceTokens] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTokens();
  }, []);

  const loadTokens = async () => {
    try {
      const tokens = await getMyDeviceTokens(authToken);
      setDeviceTokens(tokens);
    } catch (error) {
      console.error('Failed to load tokens:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveToken = async (tokenId) => {
    try {
      await unregisterDeviceToken(tokenId, authToken);
      await loadTokens();
    } catch (error) {
      console.error('Failed to remove token:', error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="notification-settings">
      <h2>Notification Settings</h2>
      <p>Registered devices:</p>
      <ul>
        {deviceTokens.map((token) => (
          <li key={token.id}>
            <span>{token.platform}</span>
            <button onClick={() => handleRemoveToken(token.id)}>
              Remove
            </button>
          </li>
        ))}
      </ul>
      {deviceTokens.length === 0 && (
        <p>No devices registered. Notifications will be enabled when you grant permission.</p>
      )}
    </div>
  );
}

export default NotificationSettings;
```

---

## Step 11: Environment Variables

Create `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-auth-domain
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-storage-bucket
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id
REACT_APP_FIREBASE_VAPID_KEY=your-vapid-key
```

Update your Firebase config to use environment variables:

```javascript
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID
};
```

---

## Step 12: Testing

### Test Notification Permission

```javascript
// Check current permission
console.log('Notification permission:', Notification.permission);

// Request permission
const permission = await Notification.requestPermission();
console.log('Permission result:', permission);
```

### Test FCM Token

```javascript
import { getFCMToken } from './services/notificationService';

const token = await getFCMToken();
console.log('FCM Token:', token);
```

### Test Backend Registration

```javascript
import { registerDeviceToken } from './services/notificationService';

const authToken = 'your-auth-token';
const fcmToken = await getFCMToken();
await registerDeviceToken(fcmToken, authToken);
```

### Test End-to-End

1. **Login** to your app
2. **Grant notification permission** when prompted
3. **Create an expense** as User A with User B as friend
4. **Check User B's browser** - should receive notification
5. **Click notification** - should navigate to expense detail

---

## Step 13: Handle Edge Cases

### Check Browser Support

```javascript
if (!('Notification' in window)) {
  console.log('This browser does not support notifications');
}

if (!('serviceWorker' in navigator)) {
  console.log('This browser does not support service workers');
}
```

### Handle Token Refresh

```javascript
import { onTokenRefresh } from 'firebase/messaging';

// Listen for token refresh
onTokenRefresh(messaging, async () => {
  const newToken = await getFCMToken();
  console.log('Token refreshed:', newToken);
  
  // Re-register with backend
  await registerDeviceToken(newToken, authToken);
});
```

### Handle Permission Changes

```javascript
// Listen for permission changes
Notification.addEventListener('change', (event) => {
  console.log('Permission changed:', event.target.permission);
  
  if (event.target.permission === 'granted') {
    // Re-initialize notifications
    initializePushNotifications(authToken);
  }
});
```

---

## Step 14: Production Checklist

- [ ] Firebase project configured
- [ ] VAPID key generated and added to code
- [ ] Service worker file created in `public/` folder
- [ ] Environment variables set for production
- [ ] HTTPS enabled (required for push notifications)
- [ ] Icons added (`icon-192x192.png`, `badge-72x72.png`)
- [ ] Notification permission requested on login
- [ ] Token registration tested
- [ ] Foreground notifications working
- [ ] Background notifications working
- [ ] Notification click navigation working
- [ ] Error handling implemented
- [ ] Token refresh handled

---

## Common Issues & Solutions

### Issue: "Messaging: We are unable to register the default service worker"

**Solution**: 
- Make sure `firebase-messaging-sw.js` is in the `public` folder
- Check that the file is accessible at `/firebase-messaging-sw.js`
- Verify service worker registration

### Issue: "getToken() failed: Messaging: This browser doesn't support the API"

**Solution**:
- Use HTTPS (required for push notifications)
- Check browser compatibility
- Verify Firebase SDK version

### Issue: Notifications not received

**Solution**:
- Check device token is registered: `GET /notifications/devices`
- Verify FCM token is valid
- Check browser console for errors
- Verify backend is sending notifications

### Issue: Service worker not registering

**Solution**:
- Check file path: `/firebase-messaging-sw.js`
- Verify file is in `public` folder
- Check browser console for errors
- Clear browser cache

---

## Complete Example: React App Integration

```javascript
// src/App.js
import React, { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { usePushNotifications } from './hooks/usePushNotifications';
import { setupForegroundMessageListener } from './services/notificationService';
import Routes from './Routes';

function App() {
  const { user, token } = useAuth();
  const { isInitialized } = usePushNotifications(token);

  useEffect(() => {
    if (isInitialized && token) {
      setupForegroundMessageListener((payload) => {
        // Handle notification
        console.log('Notification received:', payload);
        
        // Show toast or update UI
        // You can use a toast library like react-toastify
      });
    }
  }, [isInitialized, token]);

  return (
    <BrowserRouter>
      <Routes />
    </BrowserRouter>
  );
}

export default App;
```

---

## Next Steps

1. ✅ Follow steps 1-14 above
2. ✅ Test in development
3. ✅ Deploy to production (HTTPS required)
4. ✅ Monitor notification delivery
5. ✅ Collect user feedback

---

## Additional Resources

- [Firebase Cloud Messaging Docs](https://firebase.google.com/docs/cloud-messaging)
- [FCM Web Setup](https://firebase.google.com/docs/cloud-messaging/js/client)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web Push Notifications](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)

---

**Need Help?** Check the troubleshooting section or review the backend API documentation in `PUSH_NOTIFICATION_FIXES.md`.

