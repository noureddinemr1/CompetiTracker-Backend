const app = require('./app');
const dotenv = require('dotenv');
const connectDB = require('./config/db');
const path = require("path");

// Load env variables
dotenv.config();

// Connect to DB
connectDB();


const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
