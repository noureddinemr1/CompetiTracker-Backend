const express = require('express');
const cors = require('cors');
const session = require('express-session');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Session (optional – needed only if using req.session for signout)
app.use(session({
  secret: process.env.JWT_SECRET || 'supersecretkey',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false } // set to true if using HTTPS
}));

// Routes
const authRoutes = require('./routes/auth.routes');
app.use('/api/auth', authRoutes);

module.exports = app;
