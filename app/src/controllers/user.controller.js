const User = require('../models/user.model');
const bcrypt = require('bcrypt');

// Get all users
exports.getUsers = async (req, res) => {
  try {
    const users = await User.findAll();
    res.status(200).json(users);
  } catch (err) {
    res.status(500).json({ message: 'Error retrieving users', error: err });
  }
};

// Delete user by email
exports.deleteUser = async (req, res) => {
  try {
    const { email } = req.params;
    const result = await User.destroy({ where: { email } });

    if (result === 0) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.status(200).json({ message: 'User deleted successfully' });
  } catch (err) {
    res.status(500).json({ message: 'Error deleting user', error: err });
  }
};

// Accept user (change status to Active)
exports.acceptUser = async (req, res) => {
  try {
    const { email } = req.params;
    const [updated] = await User.update(
      { status: 'Active' },
      { where: { email } }
    );

    if (!updated) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.status(200).json({ message: 'User accepted' });
  } catch (err) {
    res.status(500).json({ message: 'Error accepting user', error: err });
  }
};

// Decline user (change status to Rejected)
exports.declineUser = async (req, res) => {
  try {
    const { email } = req.params;
    const [updated] = await User.update(
      { status: 'Rejected' },
      { where: { email } }
    );

    if (!updated) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.status(200).json({ message: 'User declined' });
  } catch (err) {
    res.status(500).json({ message: 'Error declining user', error: err });
  }
};

// Edit user's image and fullname
exports.editUser = async (req, res) => {
  try {
    const { email } = req.params;
    const { fullname, photo } = req.body;

    const [updated] = await User.update(
      { fullname, photo },
      { where: { email } }
    );

    if (!updated) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.status(200).json({ message: 'User updated successfully' });
  } catch (err) {
    res.status(500).json({ message: 'Error updating user', error: err });
  }
};

// Change user role
exports.changeRole = async (req, res) => {
  try {
    const { email } = req.params;
    const { role } = req.body;

    const [updated] = await User.update(
      { role },
      { where: { email } }
    );

    if (!updated) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.status(200).json({ message: 'User role updated successfully' });
  } catch (err) {
    res.status(500).json({ message: 'Error changing user role', error: err });
  }
};

// Change user password
exports.changePassword = async (req, res) => {
    try {
      const { email } = req.params;
      const { oldPassword, newPassword } = req.body;
  
      const user = await User.findOne({ where: { email } });
      if (!user) return res.status(404).json({ message: 'User not found' });
  
      const passwordMatch = await bcrypt.compare(oldPassword, user.password);
      if (!passwordMatch) {
        return res.status(401).json({ message: 'Old password is incorrect' });
      }
  
      const hashedNewPassword = await bcrypt.hash(newPassword, 10);
      await User.update({ password: hashedNewPassword }, { where: { email } });
  
      res.status(200).json({ message: 'Password changed successfully' });
    } catch (err) {
      res.status(500).json({ message: 'Error changing password', error: err });
    }
  };
   


// Change user email
exports.changeEmail = async (req, res) => {
    try {
      const { email } = req.params; // current email
      const { newEmail } = req.body;
  
      const existingUser = await User.findOne({ where: { email } });
      if (!existingUser) {
        return res.status(404).json({ message: 'User not found' });
      }
  
      const emailTaken = await User.findOne({ where: { email: newEmail } });
      if (emailTaken) {
        return res.status(409).json({ message: 'New email is already in use' });
      }
  
      await User.update({ email: newEmail }, { where: { email } });
  
      res.status(200).json({ message: 'Email updated successfully' });
    } catch (err) {
      res.status(500).json({ message: 'Error updating email', error: err });
    }
  };
  
  exports.getUserProfile = async (req, res) => {
    try {
      const user = await User.findByPk(req.userId, {
        attributes: { exclude: ['password'] }
      });
  
      if (!user) return res.status(404).json({ message: "User not found" });
  
      res.status(200).json(user);
    } catch (err) {
      res.status(500).json({ message: "Error fetching user profile", error: err });
    }
  };
  