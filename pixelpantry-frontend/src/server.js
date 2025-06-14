const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const cors = require("cors");
const fs = require("fs");
const csvParser = require("csv-parser");

const app = express();
app.use(express.json());
app.use(cors());

const CSV_FILE = "users.csv"; // CSV file to store credentials

// Function to read users from CSV
const readUsers = () => {
  return new Promise((resolve, reject) => {
    const users = [];
    fs.createReadStream(CSV_FILE)
      .pipe(csvParser())
      .on("data", (row) => users.push(row))
      .on("end", () => resolve(users))
      .on("error", reject);
  });
};

// Login Route
app.post("/api/login", async (req, res) => {
  const { email, password } = req.body;
  const users = await readUsers();
  const user = users.find((u) => u.email === email);

  if (!user || !bcrypt.compareSync(password, user.password)) {
    return res.status(401).json({ message: "Invalid email or password" });
  }

  const token = jwt.sign({ email }, "your_secret_key", { expiresIn: "1h" });
  res.json({ token });
});

// Register New User Route
app.post("/api/register", async (req, res) => {
  const { email, password } = req.body;
  const users = await readUsers();

  if (users.some((u) => u.email === email)) {
    return res.status(400).json({ message: "User already exists" });
  }

  const hashedPassword = bcrypt.hashSync(password, 10);
  fs.appendFileSync(CSV_FILE, `\n${email},${hashedPassword}`);

  res.json({ message: "User registered successfully" });
});

app.listen(5000, () => console.log("Server running on port 5000"));
