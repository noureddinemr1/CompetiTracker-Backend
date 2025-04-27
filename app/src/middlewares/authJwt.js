const jwt = require('jsonwebtoken');
const User = require('../models/user.model');

const verifyToken = (req, res, next) => {
  const token = req.headers['authorization']?.split(' ')[1];
  if (!token) {
    return res.status(403).json({ message: 'No token provided' });
  }

  jwt.verify(token, process.env.JWT_SECRET || 'supersecretkey', (err, decoded) => {
    if (err) {
      return res.status(401).json({ message: 'Unauthorized' });
    }
    req.userId = decoded.id;
    req.user = decoded;
    next();
  });
};

const isAdmin = async (req, res, next) => {
  try {
    const user = await User.findById(req.userId);
    if (!user || !['Admin', 'SuperAdmin'].includes(user.role)) {
      return res.status(403).json({ message: 'Admin or SuperAdmin access required' });
    }

    if (req.params.email) {
      const targetUser = await User.findOne({ email: req.params.email });
      if (!targetUser) {
        return res.status(404).json({ message: 'User not found' });
      }

      if (user.role === 'Admin' && ['Admin', 'SuperAdmin'].includes(targetUser.role)) {
        return res.status(403).json({ message: 'Cannot act on Admin or SuperAdmin' });
      }

      if (user.role === 'SuperAdmin' && targetUser.role === 'SuperAdmin') {
        return res.status(403).json({ message: 'Cannot act on SuperAdmin' });
      }

      if (user.id === targetUser.id) {
        return res.status(403).json({ message: 'Cannot act on self' });
      }
    }

    next();
  } catch (err) {
    res.status(500).json({ message: 'Error verifying admin access', error: err.message });
  }
};


const canEditUser = async (req, res, next) => {
  try {
    const user = await User.findByPk(req.userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    const targetEmail = req.params.email;
    const targetUser = await User.findOne({ where: { email: targetEmail } });
    if (!targetUser) {
      return res.status(404).json({ message: 'Target user not found' });
    }

    if (
      user.email === targetEmail ||
      ['Admin', 'SuperAdmin'].includes(user.role)
    ) {
      if (user.email !== targetEmail) {
        if (user.role === 'Admin' && ['Admin', 'SuperAdmin'].includes(targetUser.role)) {
          return res.status(403).json({ message: 'Cannot edit Admin or SuperAdmin' });
        }
        if (user.role === 'SuperAdmin' && targetUser.role === 'SuperAdmin') {
          return res.status(403).json({ message: 'Cannot edit SuperAdmin' });
        }
      }
      next();
    } else {
      return res.status(403).json({ message: 'Unauthorized to edit this user' });
    }
  } catch (err) {
    res.status(500).json({ message: 'Error verifying edit access', error: err.message });
  }
};

module.exports = { verifyToken, isAdmin, canEditUser };