const db = require("../models");
const User = db.user;

checkDuplicateEmail = async (req, res, next) => {
  try {
    const user = await User.findOne({
      where: { email: req.body.email }
    });

    if (user) {
      return res.status(400).json({
        message: "Failed! Email is already in use!" // Duplicate email message
      });
    }

    next();
  } catch (error) {
    return res.status(500).json({
      message: "Error occurred while checking email"
    });
  }
};

  const verifySignup = {
    checkDuplicateEmail,
  };
  
module.exports = verifySignup;