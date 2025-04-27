const { Product } = require('../models');
const mongoose = require('mongoose');

exports.getCompetitorProducts = async (req, res) => {
  try {
    const { competitor_id } = req.params;
    if (!mongoose.Types.ObjectId.isValid(competitor_id)) {
      return res.status(400).json({ message: 'Invalid competitor ID' });
    }
    const competitorObjectId = new mongoose.Types.ObjectId(competitor_id);
    const products = await Product.find({ competitor: competitorObjectId });

    if (!products || products.length === 0) {
      return res.status(404).json({ message: 'No products found for this competitor' });
    }
    res.status(200).json(products);
  } catch (err) {
    res.status(500).json({ message: 'Server error' });
  }
};

exports.getProducts = async(req,res)=>{
  try{
    const products = await Product.find();
    if (!products || products.length === 0) {
      return res.status(404).json({ message: 'No products found for this competitor' });
    }
    res.status(200).json(products);
  }catch(err){
    res.status(500).json({ message: 'Server error' });
  }
}
