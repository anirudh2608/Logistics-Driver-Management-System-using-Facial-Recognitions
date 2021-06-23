function rejectDriver(driverId) {
    fetch("reject-driver", {
        method : "POST",
        body: JSON.stringify({ driverId: driverId }), 
    }).then((_res) => {
        window.location.href = "/driverApplications";
    });
}   

function acceptDriver(driverId) {
    fetch("accept-driver", {
        method : "POST",
        body: JSON.stringify({ driverId: driverId }), 
    }).then((_res) => {
        window.location.href = "/driverApplications";
    });
}

function fireDriver(driverId) {
    fetch("fire-driver", {
        method : "POST",
        body: JSON.stringify({ driverId: driverId }), 
    }).then((_res) => {
        window.location.href = "/fireDriver";
    });
}

function deleteTruck(truckId) {
    fetch("delete-truck", {
        method : "POST",
        body: JSON.stringify({ truckId: truckId }), 
    }).then((_res) => {
        window.location.href = "/manageTrucks";
    });
}

function deleteCheckpoint(checkpointId) {
    fetch("delete-checkpoint", {
        method : "POST",
        body: JSON.stringify({ checkpointId: checkpointId }), 
    }).then((_res) => {
        window.location.href = "/driverLocation";
    });
}

function deleteOrder(orderId) {
    fetch("delete-order", {
        method : "POST",
        body: JSON.stringify({ orderId: orderId }), 
    }).then((_res) => {
        window.location.href = "/manageOrder";
    });
}

function startJourney(orderId) {
    fetch("start-journey", {
        method : "POST",
        body: JSON.stringify({ orderId: orderId }), 
    }).then((_res) => {
        window.location.href = "/dFaceRecognition";
    });
}

function trackOrder(orderId) {
    fetch("track-order", {
        method : "POST",
        body: JSON.stringify({ orderId: orderId }), 
    }).then((_res) => {
        window.location.href = "/trackOrder";
    });
}

