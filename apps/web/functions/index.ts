const functions = require("firebase-functions");
const axios = require("axios");
const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors({ origin: true }));

const baseUrls = {
  trade_execution_agent: "http://34.45.50.210:9003",
  analytics: "http://34.45.50.210:8000",
  chat: "http://34.45.50.210:8001",
  new: "http://34.30.201.70:5000",
  finance: "http://34.56.188.19:5001",
  wealth: "http://34.30.201.70:8002",
  tax: "http://34.30.201.70:8003",
  // Add more as needed
};

app.use("/:target/*", async (req, res) => {
  const target = req.params.target;
  const baseUrl = baseUrls[target];

  if (!baseUrl) {
    return res.status(400).send("Invalid target");
  }

  const path = req.originalUrl.replace(`/${target}`, "");
  const fullUrl = baseUrl + path;

  try {
    const response = await axios({
      method: req.method,
      url: fullUrl,
      data: req.body,
      headers: req.headers,
    });
    res.status(response.status).send(response.data);
  } catch (err) {
    res.status(500).send({
      error: "Proxy failed",
      details: err.message,
    });
  }
});

exports.proxy = functions.https.onRequest(app);
