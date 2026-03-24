// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCVMUi6acFH5c6In2HVbygb8gcmP8aii_s",
  authDomain: "finai-bda97.firebaseapp.com",
  projectId: "finai-bda97",
  storageBucket: "finai-bda97.firebasestorage.app",
  messagingSenderId: "440513034489",
  appId: "1:440513034489:web:51e7bf6d91da51c05b8a28",
  measurementId: "G-Z3E9LJVY51"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);


export const auth = getAuth(app);
export const db = getFirestore(app);