const controller = require('../controllers/product.controller');
const { authJwt } = require('../middlewares');
const express = require('express');
const router = express.Router();


router.get('/competitorProducts/:competitor_id', [authJwt.verifyToken], controller.getCompetitorProducts);
router.get('/products/', [authJwt.verifyToken], controller.getProducts);



module.exports = router;