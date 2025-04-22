const { verifySignup } = require("../middlewares");
const controller = require("../controllers/auth.controller");
const express = require('express');
const router = express.Router();

router.post("/signup", [verifySignup.checkDuplicateEmail], controller.signup);
router.post("/signin", controller.signin);
router.post("/signout", controller.signout);

module.exports = router;
