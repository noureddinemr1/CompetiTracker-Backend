// models/product.model.js
const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  competitor: { type: mongoose.Schema.Types.ObjectId, ref: 'Competitor', required: true },
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

const Product = mongoose.model('products', productSchema);
module.exports = Product;

