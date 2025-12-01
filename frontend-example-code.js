/**
 * FRONTEND PUSH NOTIFICATION - READY TO USE CODE
 * 
 * Copy these files to your frontend project and customize with your Firebase config
 */

// ============================================
// FILE 1: src/services/firebase.js
// ============================================

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

const app = initializeApp(firebaseConfig);

let messaging = null;
if (typeof window !== 'undefined') {
  messaging = getMessaging(app);
}

export { messaging, app };


// ============================================
// FILE 2: src/services/notificationService.js
// ============================================

import { messaging } from './firebase';
import { getToken, onMessage } from 'firebase/messaging';

const VAPID_KEY = 'YOUR_VAPID_KEY_HERE';
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function requestNotificationPermission() {
  try {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  } catch (error) {
    console.error('Error requesting permission:', error);
    return false;
  }
}

export async function getFCMToken() {
  try {
    if (!messaging) return null;
    const token = await getToken(messaging, { vapidKey: VAPID_KEY });
    return token;
  } catch (error) {
    console.error('Error getting token:', error);
    return null;
  }
}

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
          language: navigator.language
        }
      })
    });
    return await response.json();
  } catch (error) {
    console.error('Error registering token:', error);
    throw error;
  }
}

export function setupForegroundMessageListener(callback) {
  if (!messaging) return;
  
  onMessage(messaging, (payload) => {
    console.log('Message received:', payload);
    
    // Show browser notification
    if (payload.notification && Notification.permission === 'granted') {
      new Notification(payload.notification.title, {
        body: payload.notification.body,
        icon: '/icon-192x192.png'
      });
    }
    
    if (callback) callback(payload);
  });
}

export async function initializePushNotifications(authToken) {
  const hasPermission = await requestNotificationPermission();
  if (!hasPermission) return false;

  const fcmToken = await getFCMToken();
  if (!fcmToken) return false;

  await registerDeviceToken(fcmToken, authToken);
  setupForegroundMessageListener();
  
  return true;
}


// ============================================
// FILE 3: src/hooks/usePushNotifications.js
// ============================================

import { useState, useEffect } from 'react';
import { initializePushNotifications, setupForegroundMessageListener } from '../services/notificationService';

export function usePushNotifications(authToken) {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (authToken && !isInitialized) {
      setIsLoading(true);
      initializePushNotifications(authToken)
        .then((success) => {
          setIsInitialized(success);
          if (success) {
            setupForegroundMessageListener((payload) => {
              // Handle notification
              console.log('Notification:', payload);
            });
          }
        })
        .catch((error) => {
          console.error('Failed to initialize:', error);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [authToken, isInitialized]);

  return { isInitialized, isLoading };
}


// ============================================
// FILE 4: src/App.js (Example Usage)
// ============================================

import React from 'react';
import { usePushNotifications } from './hooks/usePushNotifications';

function App() {
  const authToken = localStorage.getItem('authToken');
  const { isInitialized } = usePushNotifications(authToken);

  return (
    <div className="App">
      {isInitialized && <p>✅ Notifications enabled</p>}
      {/* Your app content */}
    </div>
  );
}

export default App;


// ============================================
// FILE 5: public/firebase-messaging-sw.js
// ============================================

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
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/icon-192x192.png',
    data: payload.data
  };

  return self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  if (event.notification.data && event.notification.data.friend_id) {
    event.waitUntil(
      clients.openWindow(`/expenses/${event.notification.data.friend_id}`)
    );
  }
});


// ============================================
// FILE 6: src/index.js (Register Service Worker)
// ============================================

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

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

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);


// ============================================
// QUICK INTEGRATION (Alternative Simple Approach)
// ============================================

// Just add this to your login handler:
async function handleLogin(authToken) {
  // ... your login logic ...
  
  // Initialize notifications after login
  const permission = await Notification.requestPermission();
  if (permission === 'granted') {
    const { messaging } = await import('./services/firebase');
    const { getToken } = await import('firebase/messaging');
    
    const token = await getToken(messaging, { 
      vapidKey: 'YOUR_VAPID_KEY' 
    });
    
    await fetch('http://localhost:8000/notifications/register-device', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        token: token,
        platform: 'web'
      })
    });
  }
}

