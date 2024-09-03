const mongoose = require("mongoose");

const caseStudySchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  questions: [
    {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Question",
    },
  ],
  duration: {
    type: Number,
    required: true,
  },
  totalQuestions: {
    type: Number,
    required: true,
  },
  difficulty: {
    type: String,
    enum: ["Prarambhik", "Madhyam", "Maharathi"],
  },
});

const CaseStudy = mongoose.model("CaseStudy", caseStudySchema);

module.exports = CaseStudy;
