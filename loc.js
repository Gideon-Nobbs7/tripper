// Simple version
navigator.geolocation.getCurrentPosition(
    function(position) {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        console.log(`Location: ${lat}, ${lng}`);
    },
    function(error) {
        console.log("Location access denied or unavailable");
    }
);

// With options and error handling
const options = {
    enableHighAccuracy: true,  // Use GPS if available
    timeout: 10000,           // Wait max 10 seconds
    maximumAge: 300000        // Accept cached location up to 5 min old
};

navigator.geolocation.getCurrentPosition(success, error, options);

function success(position) {
    const coords = position.coords;
    console.log({
        latitude: coords.latitude,
        longitude: coords.longitude,
        accuracy: coords.accuracy + " meters"
    });
}

function error(err) {
    switch(err.code) {
        case err.PERMISSION_DENIED:
            alert("Location access denied by user");
            break;
        case err.POSITION_UNAVAILABLE:
            alert("Location information unavailable");
            break;
        case err.TIMEOUT:
            alert("Location request timed out");
            break;
    }
}