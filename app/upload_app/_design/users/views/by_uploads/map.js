function (doc) {
  if(doc.doc_type == "Entry") {
      emit(doc.author, [doc.original_source, doc.problem, doc.language, doc.stdout, doc.email]);
  }
}
