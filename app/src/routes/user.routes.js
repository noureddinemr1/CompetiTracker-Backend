const controller = require("../controllers/user.controller");
const {authJwt} = require("../middlewares");
const express = require('express');
const router = express.Router();


router.get("/users",[authJwt.verifyToken,authJwt.isAdmin] ,controller.getUsers);
router.get("/profile", [authJwt.verifyToken], controller.getUserProfile);
router.post("/accept/:email", [authJwt.verifyToken, authJwt.isAdmin], controller.acceptUser);
router.post("/decline/:email", [authJwt.verifyToken, authJwt.isAdmin], controller.declineUser);
router.post("/delete/:email", [authJwt.verifyToken, authJwt.isAdmin], controller.deleteUser);
router.post("/edit/:email", [authJwt.verifyToken], controller.editUser);
router.post("/changeRole/:email", [authJwt.verifyToken, authJwt.isAdmin], controller.changeRole);
router.post("/updatePassword/:email", [authJwt.verifyToken], controller.changePassword);
router.post("/updateEmail/:email", [authJwt.verifyToken], controller.changeEmail);




module.exports = router;
