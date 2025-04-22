const db = require("../models");
const User = db.user;

checkDuplicateEmail = async (req, res, next) => {
    try {
      // Email
      user = await User.findOne({
        where: {
          email: req.body.email
        }
      });
  
      if (user){
        return res.status(400).send({
          message: "Failed! Email is already in use!"
        });
      }
  
      next();
    } catch (error) {
      return res.status(500).send({
        message: error.message
      });
    }
  };

  const verifySignup = {
    checkDuplicateEmail,
  };
  
module.exports = verifySignup;