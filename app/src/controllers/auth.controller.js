const User = require('../models/user.model');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const config = require("../config/auth.config")
exports.signup = async (req, res) => {
  try {
    const { email, fullname, password } = req.body;

    const hashedPassword = await bcrypt.hash(password, 10);

    // Create a new user
    const user = new User({
      email,
      password: hashedPassword,
      fullname,
      role: 'None',
      status: 'Pending',
    });

    await user.save(); // Save user to the database

    // Return success message after user creation
    res.status(200).json({ message: 'User registered successfully. Awaiting admin approval.' });
  } catch (err) {
    // This error is for unexpected issues during the user creation
    res.status(500).json({ message: 'Registration failed!' });
  }
};



exports.signin = async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findByEmail(email);

    if (!user) {
      return res.status(404).json({ message: 'User not found.' });
    }

    if (user.status !== 'Active') {
      return res.status(403).json({ message: 'Account not active. Please wait for approval.' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ message: 'Invalid password.' });
    }


    const token = jwt.sign(
      { id: user._id, email: user.email, role: user.role},
      config.secret || 'secret-key',
      { expiresIn: '24h' }
    );

    res.status(200).json({
      id: user._id,
      email: user.email,
      fullname: user.fullname,
      role: user.role,
      status : user.status,
      token,
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

exports.signout = async (req, res) => {
  try {
    req.session = null;
    res.status(200).json({ message: "You've been signed out." });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
