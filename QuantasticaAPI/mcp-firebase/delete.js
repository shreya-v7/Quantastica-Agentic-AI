const admin = require("firebase-admin");
const serviceAccount = require("./../serviceAccountKey.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const db = admin.firestore();

async function deleteCollection(collectionPath) {
  const collectionRef = db.collection(collectionPath);
  const docs = await collectionRef.listDocuments();

  for (const doc of docs) {
    await doc.delete();
    console.log(`Deleted doc ${doc.id} from ${collectionPath}`);
  }
}

async function clearAll() {
  // List your top-level collections here
  const collections = await db.listCollections();

  for (const collection of collections) {
    console.log(`Deleting collection: ${collection.id}`);
    await deleteCollection(collection.id);
  }

  console.log("All top-level collections deleted");
}

clearAll().catch(console.error);
