const controller = require('../controllers/user.controller');
const { authJwt } = require('../middlewares');
const { upload } = require('../middlewares');
const express = require('express');
const router = express.Router();


router.get('/users', [authJwt.verifyToken, authJwt.isAdmin], controller.getUsers);
router.get('/profile/:email', [authJwt.verifyToken], controller.getUserProfile);
router.put('/accept/:email', [authJwt.verifyToken, authJwt.isAdmin], controller.acceptUser);
router.put('/decline/:email', [authJwt.verifyToken, authJwt.isAdmin], controller.declineUser);
router.delete('/delete/:email', [authJwt.verifyToken, authJwt.isAdmin], controller.deleteUser);
router.post("/edit/:email", [upload.single("photo")], controller.editUser);
router.put('/changeRole/:email', [authJwt.verifyToken, authJwt.isAdmin], controller.changeRole);
router.post('/updatePassword/:email', [authJwt.verifyToken], controller.updatePassword);
router.post('/updateEmail/:email', [authJwt.verifyToken], controller.updateEmail);
router.post("/editprofile/:email",[authJwt.verifyToken,upload.single("photo")], controller.editProfile)

module.exports = router;