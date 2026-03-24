import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  onAuthStateChanged,
} from "firebase/auth";
import { doc, setDoc } from "firebase/firestore";
import { auth, db } from "../auth/firebase";
import { useNavigate } from "react-router";


const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const [isSignup, setIsSignup] = useState(false);
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isSignup) {
        if (formData.password !== formData.confirmPassword) {
          alert("Passwords do not match!");
          setLoading(false);
          return;
        }

        const userCred = await createUserWithEmailAndPassword(
          auth,
          formData.email,
          formData.password
        );
        const uid = userCred.user.uid;

        await setDoc(doc(db, "users", uid), {
          fullName: formData.fullName,
          email: formData.email,
          phone: formData.phone,
          createdAt: new Date().toISOString(),
        });

        localStorage.setItem("userId", uid);
        alert("Signup successful!");
        navigate("/dashboard");
      } else {
        const userCred = await signInWithEmailAndPassword(
          auth,
          formData.email,
          formData.password
        );
        const uid = userCred.user.uid;
        localStorage.setItem("userId", uid);
        alert("Login successful!");
        navigate("/dashboard");
      }
    } catch (error: any) {
      console.error("Auth Error:", error);
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        console.log("User is logged in:", user.uid);
        localStorage.setItem("userId", user.uid);
      } else {
        console.log("User is logged out.");
        localStorage.removeItem("userId");
      }
    });

    return () => unsubscribe();
  }, []);

  return (
    
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#080e2a] via-[#0b132b] to-[#10142d] px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md p-8 rounded-2xl bg-[#151c3b]/70 backdrop-blur-xl shadow-[0_0_30px_#0ea5e9] border border-blue-500/30"
      >
        <h2 className="text-3xl font-bold text-center mb-6 text-white drop-shadow-lg">
          {isSignup ? "Create Your Account" : "Welcome"}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5">
          {isSignup && (
            <>
              <Input
                label="Full Name"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
              />
              <Input
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
              />
            </>
          )}

          {!isSignup && (
            <Input
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
            />
          )}

          <Input
            label="Phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="+91 9876543210"
          />
          <Input
            label="Password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
          />
          {isSignup && (
            <Input
              label="Confirm Password"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
            />
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold shadow-lg hover:shadow-[0_0_20px_#38bdf8] rounded-lg transition-all"
          >
            {loading ? "Please wait..." : isSignup ? "Sign Up" : "Login"}
          </button>
        </form>

        <div className="text-center mt-6 text-sm text-gray-400">
          {isSignup ? "Already have an account?" : "Don’t have an account?"}{" "}
          <button
            onClick={() => setIsSignup(!isSignup)}
            className="text-blue-400 hover:underline hover:text-blue-300 transition"
          >
            {isSignup ? "Login" : "Sign Up"}
          </button>
        </div>
      </motion.div>
    </div>
  );
};

const Input = ({
  label,
  name,
  value,
  onChange,
  type = "text",
  placeholder = "",
}: {
  label: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  placeholder?: string;
}) => (
  <div className="text-left">
    <label className="block mb-1 text-sm text-blue-300">{label}</label>
    <input
      type={type}
      name={name}
      required
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className="w-full px-4 py-2 rounded-lg bg-[#0d1325] text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:shadow-[0_0_10px_#0ea5e9] transition-all"
    />
  </div>
);

export default AuthPage;
