function(req, res) {
    provides('json', function() {
        var results = [];
        while(row = getRow()) {
            results.push({
                points: row.value[0],
                duration: row.value[1],
                username: row.key[1],
                grade: row.key[0],
                email: row.key[2],
                problem: row.key[3],
                language: row.key[6]
            });
        }
        send(JSON.stringify(results));
    });
}
