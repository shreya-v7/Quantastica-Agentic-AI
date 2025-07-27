const express = require("express");
const cors = require("cors");
const admin = require("firebase-admin");
const serviceAccount = require("./../serviceAccountKey.json");

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

// Initialize Firebase
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const db = admin.firestore();

/**
 * 🔁 Reusable function to fetch document from Firestore
 * @param {string} phone - phone number (Firestore user ID)
 * @param {string} docName - name of the document to fetch (e.g., fetch_mf_transactions)
 * @returns {object|null} - returns data or null if not found
 */
const fetchUserDocument = async (phone, docName) => {
  try {
    const docRef = db
      .collection("users")
      .doc(phone)
      .collection("data")
      .doc(docName)
      .collection("items")
      .doc("singleton");

    const docSnap = await docRef.get();

    if (!docSnap.exists) {
      return null;
    }

    return docSnap.data();
  } catch (err) {
    console.error("Error fetching Firestore doc:", err);
    throw err;
  }
};

// ✅ Test route
app.get("/api/test", (req, res) => {
  res.json({ message: "Test endpoint is working!" });
});

// 📦 Generic endpoint
// Example: /api/user/1010101010/fetch_mf_transactions
app.get("/api/user/:phone/:docName", async (req, res) => {
  const { phone, docName } = req.params;

  try {
    const data = await fetchUserDocument(phone, docName);

    if (!data) {
      return res.status(404).json({ message: "Document not found" });
    }

    res.json({ data });
  } catch (err) {
    res.status(500).json({ message: "Internal server error" });
  }
});

app.listen(port, () => {
  console.log(`🚀 Server running at http://localhost:${port}`);
});
