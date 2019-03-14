function (doc) {
  if (doc.doc_type == "Entry" && doc.tested == 1) {
      emit([doc.problem, doc.grade, doc.points, doc.total, doc.language, doc.author, doc.email], 1);
  }
}
