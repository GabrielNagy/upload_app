function (doc) {
    if (doc.username && doc.email && doc.date && doc.grade) {
        emit(doc.username, [doc.password, doc.grade, doc.admin])
    }
}
