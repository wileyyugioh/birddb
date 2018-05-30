SEARCH_NAME = "search";
COORD_NAME = "latlon";
LAT_NAME = "form-lat";
LON_NAME = "form-lon";
SEARCH_FORM_NAME = "form-search";
DROPDOWN = "dropdown"

lat_dom = document.getElementById(LAT_NAME);
lon_dom = document.getElementById(LON_NAME);
search_form_dom = document.getElementById(SEARCH_FORM_NAME);
search_dom = document.getElementById(SEARCH_NAME);
coord_dom = document.getElementById(COORD_NAME);
drop_dom = document.getElementById(DROPDOWN);
search_parent_dom = search_form_dom.parentNode;


function updateFormLocation(lat, lon) {
    lat_dom.value = lat.toString().substring(0, 10);
    lon_dom.value = lon.toString().substring(0, 10);
}

function showSearch() {
    lat_dom.parentNode.style.display = "none";
    lon_dom.parentNode.style.display = "none";
    search_parent_dom.style.display = "";
}

function showCoord() {
    lat_dom.parentNode.style.display = "";
    lon_dom.parentNode.style.display = "";
    search_parent_dom.style.display = "none";
}

function clearDrops() {
    while(drop_dom.firstChild) {
        drop_dom.removeChild(drop_dom.firstChild);
    }
}

function addDrop(word, lat, lon) {
    var dropdown = document.createElement("a");
    dropdown.className = "dropdown-content"
    dropdown.innerHTML = word;
    drop_dom.appendChild(dropdown);

    dropdown.addEventListener("click", function() {
        updateFormLocation(lat, lon);
        coord_dom.checked = true;
        showCoord();
    }, false);
}

function _doResults(json_data) {
    clearDrops();
    var features = json_data["features"];
    var found = [];
    for(var i = 0; i < features.length; i++) {
        var name_block = features[i];
        var properties = name_block["properties"];
        if(properties["osm_value"] === "city" || properties["osm_value"] === "town")
        {
            var coords = name_block["geometry"]["coordinates"];
            var display_name = properties["name"] + ", " + properties["state"] + ", " + properties["country"];
            if(!found.includes(display_name)) {
                addDrop(display_name, coords[1], coords[0]);
                found.push(display_name);
            }
        }
    }
}

function getResults(location_string) {
    if(location_string === "") {
        clearDrops();
        return;
    }

    var script_url = "https://photon.komoot.de/api/?limit=5&q=" + location_string;
    fetch(script_url)
    .then(res => res.json())
    .then((out) => {
        _doResults(out)
    })
    .catch(err => {throw err});
}

function main() {
    showSearch();
    search_dom.checked = true;
    search_dom.disabled = false;

    search_dom.addEventListener("click", function() {
        showSearch();
    }, false);

    coord_dom.addEventListener("click", function() {
        showCoord();
    }, false);

    var search_timer = null;
    search_form_dom.addEventListener("keydown", function() {
        clearTimeout(search_timer);
        search_timer = setTimeout(function() {
            getResults(search_form_dom.value);
        }, 250);

    }, false);

    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(function(position) {
            showCoord();
            coord_dom.checked = true;
            updateFormLocation(position.coords.latitude, position.coords.longitude)
        });
    }
}

main();