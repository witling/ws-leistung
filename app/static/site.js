document.addEventListener("DOMContentLoaded", function () {
    const MIN_SEARCH_LENGTH = 3;

    function error() {
        let bar = document.getElementById("searchbar");
        let note = new bootstrap.Popover(bar, {
            animation: false,
            content: `Search query must be at least ${MIN_SEARCH_LENGTH} characters long.`,
            customClass: "border border-danger",
            placement: "bottom",
            trigger: "focus"
        });
        console.log(this.response, this.status);
    }

    function validate(event) {
        let len = document.getElementById("searchbar").value.trim().length
        if (len < MIN_SEARCH_LENGTH) {
            error();
            event.preventDefault();
        }
    }

    function fetchBackground(url, callback) {
        let request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            if (this.readyState === XMLHttpRequest.DONE) {
                callback(this.response, this.status);
            }
        };
        request.open("GET", url);
        console.log(`fetching url ${url} ...`);
        request.send();
    }

    function addGalleries(response) {
        console.log(response.status);
        let galleries = JSON.parse(response);
        let galleryDropdownSelect = document.getElementById("galleryDropdownSelect");
        let imageId = document.getElementById("imageId").value;
        for (let gallery of galleries) {
            let node = document.createElement("button");

            node.type = "button";
            node.className = "dropdown-item";
            node.innerText = gallery.name;
            node.addEventListener("click", function (event) {
                let url = `/api/gallery/${gallery.id}/add?image_id=${imageId}`;
                fetchBackground(url, function (response, statusCode) {
                    if (statusCode === 200) {
                        alert("Image was added to the gallery.");
                    } else {
                        alert("There was an error while adding the image to the gallery.");
                    }
                });

                event.preventDefault();
            });

            galleryDropdownSelect.appendChild(node);
        }
    }

    let galleryDropdownOpen = document.getElementById("galleryDropdownOpen");
    if (galleryDropdownOpen !== null) {
        fetchBackground("/api/galleries", addGalleries);
    }

    document.getElementById("searchform").addEventListener("submit", validate);
});
