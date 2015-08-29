exports.pingme = function (data) {
    var d = new Date();
    output = {
        "IP_address" : data.ip,
        "timestamp"  : d.getTime(),
        "name" : data.name,
    }
    return output;   
};

