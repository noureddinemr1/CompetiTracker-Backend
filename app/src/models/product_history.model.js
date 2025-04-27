// models/productHistory.model.js
const mongoose = require('mongoose');

const productHistorySchema = new mongoose.Schema({
  product: { type: mongoose.Schema.Types.ObjectId, ref: 'Product', required: true },
  competitor: { type: mongoose.Schema.Types.ObjectId, ref: 'Competitor', required: true },
  price: { type: String, required: true },
  stock_status: { type: String, required: true },
  scrapedAt: { type: Date, default: Date.now }
});

const ProductHistory = mongoose.model('product_history', productHistorySchema);
module.exports = ProductHistory;
