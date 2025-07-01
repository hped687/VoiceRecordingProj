const express = require('express');
const cors = require('cors');
const multer = require('multer');

const app = express();
const port = process.env.PORT || 3000;

// Enable CORS for all origins (or specify your domain)
app.use(cors({
  origin: '*', // You can restrict to Netlify domain for security
}));

// Handle multipart/form-data
const upload = multer();

app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  // Example: log or save the file (for now just respond success)
  console.log(`Received file: ${req.file.originalname}`);
  res.status(200).send('File uploaded successfully');
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
