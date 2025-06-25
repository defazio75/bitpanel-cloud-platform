// src/firebaseConfig.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyCUW_tZ5vk4zKD2_GGo1-DJ6DfdaKGIXUw",
  authDomain: "bitpanel-967b1.firebaseapp.com",
  databaseURL: "https://bitpanel-967b1-default-rtdb.firebaseio.com",
  projectId: "bitpanel-967b1",
  storageBucket: "bitpanel-967b1.firebasestorage.app",
  messagingSenderId: "633698121406",
  appId: "1:633698121406:web:d1e72d97789635135e50ef"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { auth };
