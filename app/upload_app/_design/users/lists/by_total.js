function(req, res) {
    provides('json', function() {
        var results = [];
        while(row = getRow()) {
            results.push({
                points: row.value[0],
                duration: row.value[1],
                username: row.key[1],
                grade: row.key[0],
                email: row.key[2]
            });
        }
        var sorted = results.sort(function (x, y) { return x.points - y.points || x.duration - y.duration; });
        send(JSON.stringify(sorted));
    });
}
