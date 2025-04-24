const jwt = require("jsonwebtoken");
const config = require("../config/auth.config.js");
const User = require("../models/user.model"); // <-- Import User model

// Middleware to verify JWT token
verifyToken = (req, res, next) => {
  let token = req.session.token;

  if (!token) {
    return res.status(403).send({
      message: "No token provided!",
    });
  }

  jwt.verify(token, config.secret, (err, decoded) => {
    if (err) {
      return res.status(401).send({
        message: "Unauthorized!",
      });
    }
    req.userId = decoded.id;
    next();
  });
};

// Middleware to check if user is admin
isAdmin = async (req, res, next) => {
  try {
    const user = await User.findByPk(req.userId); // or use findOne with where: { id: req.userId }
    if (!user) {
      return res.status(404).send({ message: "User not found." });
    }

    if (user.role !== "Admin" && user.role !=="SuperAdmin") {
      return res.status(403).send({
        message: "Require Admin Role!",
      });
    }

    next(); 
  } catch (error) {
    return res.status(500).send({
      message: "Unable to validate Admin role!",
    });
  }
};

isSuperAdmin = async (req, res, next) => {
  try {
    const user = await User.findByPk(req.userId); // or use findOne with where: { id: req.userId }
    if (!user) {
      return res.status(404).send({ message: "User not found." });
    }

    if (user.role !== "SuperAdmin") {
      return res.status(403).send({
        message: "Require Admin Role!",
      });
    }

    next(); 
  } catch (error) {
    return res.status(500).send({
      message: "Unable to validate Admin role!",
    });
  }
};

const authJwt = {
  verifyToken,
  isAdmin, 
  isSuperAdmin,
};

module.exports = authJwt;
