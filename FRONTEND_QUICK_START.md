# Frontend Push Notification - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### 1. Install Firebase
```bash
npm install firebase
```

### 2. Create Firebase Config File

`src/services/firebase.js`:
```javascript
import { initializeApp } from 'firebase/app';
import { getMessaging } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
const messaging = typeof window !== 'undefined' ? getMessaging(app) : null;

export { messaging };
```

### 3. Create Notification Service

`src/services/notifications.js`:
```javascript
import { messaging } from './firebase';
import { getToken } from 'firebase/messaging';

const VAPID_KEY = 'YOUR_VAPID_KEY';
const API_URL = 'http://localhost:8000';

export async function setupNotifications(authToken) {
  // Request permission
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') return false;

  // Get FCM token
  const fcmToken = await getToken(messaging, { vapidKey: VAPID_KEY });
  if (!fcmToken) return false;

  // Register with backend
  await fetch(`${API_URL}/notifications/register-device`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({
      token: fcmToken,
      platform: 'web'
    })
  });

  return true;
}
```

### 4. Call on Login

```javascript
import { setupNotifications } from './services/notifications';

// After user logs in
await setupNotifications(authToken);
```

### 5. Create Service Worker

`public/firebase-messaging-sw.js`:
```javascript
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  return self.registration.showNotification(
    payload.notification.title,
    {
      body: payload.notification.body,
      icon: '/icon-192x192.png'
    }
  );
});
```

### 6. Register Service Worker

In your `src/index.js` or `src/main.js`:
```javascript
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/firebase-messaging-sw.js');
}
```

---

## 📋 Checklist

- [ ] Firebase project created
- [ ] VAPID key generated (Firebase Console → Cloud Messaging)
- [ ] Firebase config added to code
- [ ] Service worker file created
- [ ] Notification permission requested
- [ ] Device token registered with backend
- [ ] Test: Create expense → Friend receives notification

---

## 🔑 Where to Find VAPID Key

1. Firebase Console → Your Project
2. Project Settings ⚙️
3. Cloud Messaging tab
4. Web Push certificates section
5. Copy the key (or generate if not exists)

---

## 🧪 Test It

```javascript
// 1. Get token
const token = await getToken(messaging, { vapidKey: VAPID_KEY });
console.log('Token:', token);

// 2. Register with backend
await setupNotifications(authToken);

// 3. Create expense (as User A)
// 4. Check User B's browser for notification
```

---

## ⚠️ Important Notes

- **HTTPS Required**: Push notifications only work on HTTPS (or localhost)
- **Service Worker**: Must be in `public/` folder
- **VAPID Key**: Get from Firebase Console
- **Permission**: User must grant notification permission

---

## 🐛 Common Issues

**"Messaging not initialized"**
→ Check if `typeof window !== 'undefined'`

**"Service worker not found"**
→ Make sure file is in `public/` folder

**"Token is null"**
→ Check VAPID key is correct
→ Verify HTTPS (or localhost)

**"Notifications not received"**
→ Check device token registered: `GET /notifications/devices`
→ Verify backend is sending notifications

---

## 📚 Full Guide

See `FRONTEND_PUSH_NOTIFICATION_GUIDE.md` for complete documentation.
