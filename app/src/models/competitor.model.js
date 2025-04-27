// models/competitor.model.js
const mongoose = require('mongoose');

const competitorSchema = new mongoose.Schema({
  name: { type: String, required: true },
  url: { type: String, required: true },
  logo: { type: String, required: true }
});

const Competitor = mongoose.model('competitors', competitorSchema);
module.exports = Competitor;