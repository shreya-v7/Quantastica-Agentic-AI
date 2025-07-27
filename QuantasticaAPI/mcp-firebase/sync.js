const admin = require("firebase-admin");
const fs = require("fs");
const path = require("path");

const serviceAccount = require("./../serviceAccountKey.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const db = admin.firestore();


function mapTxnArrayToObject(txnArr) {
  // Map array to object using schema
  return {
    transactionAmount: txnArr[0],
    transactionNarration: txnArr[1],
    transactionDate: txnArr[2],
    transactionType: txnArr[3],
    transactionMode: txnArr[4],
    currentBalance: txnArr[5]
  };
}

function mapMfTxnArrayToObject(txnArr) {
  return {
    orderType: txnArr[0],
    transactionDate: txnArr[1],
    purchasePrice: txnArr[2],
    purchaseUnits: txnArr[3],
    transactionAmount: txnArr[4]
  };
}
function mapStockTxnArrayToObject(txnArr) {
  return {
    transactionType: txnArr[0],
    transactionDate: txnArr[1],
    quantity: txnArr[2],
    navValue: txnArr.length > 3 ? txnArr[3] : null
  };
}

function sanitizeForFirestore(value) {
  if (value === null) return null;

  if (Array.isArray(value)) {
    // Detect if this is a stock txn array (3 or 4 elements, first is number)
    if (
      (value.length === 3 || value.length === 4) &&
      typeof value[0] === "number" &&
      typeof value[1] === "string"
    ) {
      return mapStockTxnArrayToObject(value);
    }
    // Detect if this is a MF txn array (5 elements, first is number)
    if (
      value.length === 5 &&
      typeof value[0] === "number" &&
      typeof value[1] === "string"
    ) {
      return mapMfTxnArrayToObject(value);
    }
    // Detect if this is a bank txn array (6 elements, first is string)
    if (
      value.length === 6 &&
      typeof value[0] === "string" &&
      typeof value[3] === "number"
    ) {
      return mapTxnArrayToObject(value);
    }
    return value.map(sanitizeForFirestore).filter((v) => v !== undefined);
  }

  if (typeof value === "object") {
    const sanitized = {};
    for (const [key, val] of Object.entries(value)) {
      sanitized[key] = sanitizeForFirestore(val);
    }
    return sanitized;
  }

  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return value;
  }

  return undefined;
}

async function syncAll() {
  const dataRoot = path.join(__dirname, "test_data_dir");

  const phoneDirs = fs
    .readdirSync(dataRoot)
    .filter((name) => fs.statSync(path.join(dataRoot, name)).isDirectory());

  for (const phone of phoneDirs) {
    const phoneDirPath = path.join(dataRoot, phone);
    const files = fs.readdirSync(phoneDirPath).filter((f) => f.endsWith(".json"));

    for (const file of files) {
      const filePath = path.join(phoneDirPath, file);
      const fileName = path.basename(file, ".json");

      try {
        const rawData = fs.readFileSync(filePath, "utf8").trim();

        if (!rawData) {
          console.warn(`⚠️ Skipped empty file: ${filePath}`);
          continue;
        }

        let parsed;
        try {
          parsed = JSON.parse(rawData);
        } catch {
          console.warn(`⚠️ Invalid JSON: ${filePath}`);
          continue;
        }

        if (
          typeof parsed !== "object" ||
          parsed === null ||
          (Array.isArray(parsed) && parsed.length === 0) ||
          (!Array.isArray(parsed) && Object.keys(parsed).length === 0)
        ) {
          console.warn(`⚠️ Skipped empty JSON object/array: ${filePath}`);
          continue;
        }

        const sanitized = sanitizeForFirestore(parsed);

        const collectionRef = db
          .collection("users")
          .doc(phone)
          .collection("data")
          .doc(fileName)
          .collection("items");

        // Delete old docs before sync
        const oldDocs = await collectionRef.listDocuments();
        for (const doc of oldDocs) {
          await doc.delete();
        }

        if (Array.isArray(sanitized)) {
          // One document per array item
          const batch = db.batch();
          sanitized.forEach((item, idx) => {
            batch.set(collectionRef.doc(idx.toString()), item);
          });
          await batch.commit();
        } else {
          // Single object stored as 'singleton'
          await collectionRef.doc("singleton").set(sanitized);
        }

        console.log(`✅ Synced ${filePath} to users/${phone}/data/${fileName}/items`);
      } catch (err) {
        console.error(`❌ Error syncing ${filePath}:`, err.message);
      }
    }
  }
}

syncAll().catch(console.error);
