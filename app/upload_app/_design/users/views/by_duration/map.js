function (doc) {
  if (doc.doc_type == "Entry" && doc.duration) {
  emit(doc.duration, doc.author);
  }
}
