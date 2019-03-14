function (doc) {
    if (doc.doc_type == "Entry" && doc.author && doc.problem) {
        emit([doc.author, doc.problem], 1);
    }
}
