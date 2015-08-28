exports.pingme = function (data) {
    var d = new Date();
    output = {
        "IP_address" : data.ip,
        "timestamp"  : d.getTime(),
    }
    return output;   
};
