// src/services/authService.ts
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "firebase/auth";
import { setDoc, doc } from "firebase/firestore";
import { auth, db } from "../auth/firebase";
// Sign up user
export const signUp = async (
  email: string,
  password: string,
  fullName: string,
  phone: string
): Promise<string> => {
  if (!email || !password || !fullName || !phone) {
    throw new Error("All fields are required.");
  }

  try {
    const cred = await createUserWithEmailAndPassword(auth, email, password);
    await setDoc(doc(db, "users", cred.user.uid), {
      fullName,
      email,
      phone,
      createdAt: new Date().toISOString(),
    });

    localStorage.setItem("userId", cred.user.uid);
    return cred.user.uid;
  } catch (error: any) {
    console.error("Sign up failed:", error.message);
    throw new Error(error.message);
  }
};

// Login user
export const login = async (
  email: string,
  password: string
): Promise<string> => {
  if (!email || !password) {
    throw new Error("Email and password are required.");
  }

  try {
    const cred = await signInWithEmailAndPassword(auth, email, password);
    localStorage.setItem("userId", cred.user.uid);
    return cred.user.uid;
  } catch (error: any) {
    console.error("Login failed:", error.message);
    throw new Error(error.message);
  }
};

// Logout user
export const logout = async (): Promise<void> => {
  try {
    await signOut(auth);
    localStorage.removeItem("userId");
  } catch (error: any) {
    console.error("Logout failed:", error.message);
    throw new Error(error.message);
  }
};

// Get current logged-in user ID
export const getCurrentUserId = (): string | null => {
  return localStorage.getItem("userId");
};
