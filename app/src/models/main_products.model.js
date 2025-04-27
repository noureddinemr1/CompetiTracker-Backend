// models/product.model.js
const mongoose = require('mongoose');

const mainProductSchema = new mongoose.Schema({
  url: { type: String, required: true },
  product_name: { type: String, required: true },
  product_price: { type: String, required: true },
  discount: { type: String, default: "No Discount" },
  category: { type: String, required: true },
  stock_status: { type: String, required: true },
  ref: { type: String, required: true },
  description: { type: String, required: true },
  livraison: { type: String, default: "Gratuite" },
  image: { type: String, required: true },
  LastUpdate: { type: Date, default: Date.now }
});

const MainProduct = mongoose.model('our_products', mainProductSchema);
module.exports = MainProduct;

