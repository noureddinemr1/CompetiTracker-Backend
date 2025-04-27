const User = require('../models/user.model');
const bcrypt = require('bcrypt');

// Get all users
exports.getUsers = async (req, res) => {
  try {
    const users = await User.find().select("-password");
    res.status(200).json(users);
  } catch (err) {
    res.status(500).json({ message: 'Error retrieving users'});
  }
};

// Delete user by email
exports.deleteUser = async (req, res) => {
  try {
    const email = req.params.email;

    const result = await User.findOneAndDelete({ email: email });

    if (!result) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.status(200).json({ message: 'User deleted successfully' });
  } catch (err) {
    res.status(500).json({ message: 'Error deleting user'});
  }
};


// Accept user
exports.acceptUser = async (req, res) => {
  try {
    const email = req.params.email;

    // Find the user
    const user = await User.findOne({email : email}).select("-password");

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Update the fields
    user.status = 'Active';
    user.role = 'Marketing Analyst';

    // Save changes
    await user.save();

    // Exclude password before sending response
    const userData = user.toJSON();

    res.status(200).json({ message: 'User accepted', user: userData });
  } catch (err) {
    res.status(500).json({ message: 'Error accepting user' });
  }
};

// Decline user
exports.declineUser = async (req, res) => {
  try {
    const email = req.params.email;

    // Find the user
    const user = await User.findOne({email : email}).select("-password");

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Update the fields
    user.status = 'Rejected';
    user.role = 'None';

    // Save changes
    await user.save();

    res.status(200).json({ message: 'User declined', user });
  } catch (err) {
    res.status(500).json({ message: 'Error declining user'});
  }
};

// Edit user's image and fullname
exports.editUser = async (req, res) => {
  try {
    const { email } = req.params;
    const { fullname } = req.body;
    const photo = req.file ? `/uploads/${req.file.filename}` : req.body.photo;

    const user = await User.findOne({email : email}).select("-password");

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Update the fields
    user.fullname = fullname;
    user.photo = photo;

    // Save changes
    await user.save();

    res.status(200).json({ message: "User updated successfully", user });
  } catch (err) {
    res.status(500).json({ message: "Error updating user"});
  }
};

// Change user role
exports.changeRole = async (req, res) => {
  try {
    const { email } = req.params;
    const { role } = req.body;
    const validRoles = ['Admin', 'Marketing Analyst'];

    if (!validRoles.includes(role)) {
      return res.status(400).json({ message: 'Invalid role' });
    }

    const user = await User.findOne({email : email}).select("-password");
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Update the fields
    user.role = role;
    // Save changes
    await user.save();
    

    res.status(200).json({ message: 'User role updated successfully', user });
  } catch (err) {
    res.status(500).json({ message: 'Error changing user role'});
  }
};

// Change user password
exports.updatePassword = async (req, res) => {
  try {
    const { email } = req.params;
    const { oldPassword, newPassword } = req.body;

    if (!oldPassword || !newPassword) {
      return res.status(400).json({ message: 'Old and new passwords are required' });
    }

    const user = await User.findOne({email : email});
    if (!user) return res.status(404).json({ message: 'User not found' });

    const passwordMatch = await bcrypt.compare(oldPassword, user.password);
    if (!passwordMatch) {
      return res.status(401).json({ message: 'Old password is incorrect' });
    }

    const hashedNewPassword = await bcrypt.hash(newPassword, 10);
    user.password = hashedNewPassword;
    await user.save();
    res.status(200).json({ message: 'Password changed successfully' });
  } catch (err) {
    res.status(500).json({ message: 'Error changing password'});
  }
};

// Change user email
exports.updateEmail = async (req, res) => {
  try {
    const { email } = req.params;
    const { newEmail } = req.body;

    if (!newEmail) {
      return res.status(400).json({ message: 'New email is required' });
    }

    const existingUser = await User.findOne({email : email}).select("-password");
    if (!existingUser) {
      return res.status(404).json({ message: 'User not found' });
    }

    const emailTaken = await User.findOne({email : newEmail});
    if (emailTaken) {
      return res.status(409).json({ message: 'New email is already in use' });
    }

    existingUser.email = newEmail;
    await existingUser.save();
    res.status(200).json({ message: 'Email updated successfully', existingUser });
  } catch (err) {
    res.status(500).json({ message: 'Error updating email'});
  }
};

// Get user profile
exports.getUserProfile = async (req, res) => {
  try {
    const {email} = req.params;
    const user = await User.findOne({email : email}).select("-password");

    if (!user) return res.status(404).json({ message: 'User not found' });
    res.status(200).json(user);
  } catch (err) {
    res.status(500).json({ message: 'Error fetching user profile' });
  }
};


exports.editProfile = async(req,res) =>{
  try{
    const {email} = req.params;
    const {fullname,phoneNumber} = req.body;
    const photo = req.file ? `/uploads/${req.file.filename}` : req.body.photo;
    const user = await User.findOne({email : email});
    if (!user) return res.status(404).json({ message: 'User not found' });
    user.photo = photo;
    user.fullname = fullname;
    user.phoneNumber = phoneNumber;
    await user.save();
    res.status(200).json({ message: 'User updated successfully' });
  }catch(err){
    res.status(500).json({message : "Error editing profile"});
  }
}