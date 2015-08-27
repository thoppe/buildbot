function pingme(data) {
    var d = new Date();
    output = {
        "IP_address" : data.ip,
        "timestamp"  : d.getTime(),
    }
    return output;
    
};

//example_data = {"ip":"98.207.254.136"}
//console.log(pingme(example_data));
