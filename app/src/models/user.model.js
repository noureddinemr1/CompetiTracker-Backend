const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  fullname: { type: String },
  role: { type: String, default: 'None' },
  status: { type: String, default: 'Pending' },
  photo: { type: String },
  phoneNumber : {type : String},
}, { timestamps: true }); 


userSchema.statics.findByEmail = function(email) {
  return this.findOne({ email });
};


const User = mongoose.model('users', userSchema);
module.exports = User;
