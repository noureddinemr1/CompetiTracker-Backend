// models/urls.model.js
const mongoose = require('mongoose');

const urlsSchema = new mongoose.Schema({
  competitor: { type: mongoose.Schema.Types.ObjectId, ref: 'Competitor', required: true },
  scrapedAt: { type: Date, default: Date.now },
  urls: { type: [String], required: true }
});

const Urls = mongoose.model('urls', urlsSchema);
module.exports = Urls;
