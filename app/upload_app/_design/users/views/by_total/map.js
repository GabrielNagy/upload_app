function(doc) {
  if (doc.doc_type == "Entry" && doc.total) {
      emit([doc.grade, doc.author, doc.email, doc.problem, doc.points, doc.total, doc.language], [doc.points, doc.total]);
 }
}
