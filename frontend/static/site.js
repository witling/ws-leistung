document.addEventListener("DOMContentLoaded", function () {
    const MIN_SEARCH_LENGTH = 3;
    const TOAST_CONTAINER_ID = "custom-alerts-container";

    function createUUID() {
        return Date.now().toString(36) + Math.random().toString(36).substring(2);
    }

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
                let url = `/api/gallery/${gallery.id}/add/${imageId}`;
                fetchBackground(url, function (response, statusCode) {
                    console.log(response)
                    if (statusCode === 200) {
                        pushToast(`Image was added to gallery "${gallery.name}".`, "success");
                    } else {
                        pushToast("There was an error while adding the image to the gallery.", "error")
                    }
                });

                event.preventDefault();
            });

            galleryDropdownSelect.appendChild(node);
        }
    }

    function pushToast(msg, ty) {
        let uuid = createUUID();

        let node = document.createElement("div");
        node.id = `toast-notice-${uuid}`;
        node.className = "toast";
        node.setAttribute("role", "alert");
        node.setAttribute("aria-live", "assertive");
        node.setAttribute("aria-atomic", "true");

        switch (ty) {
            case "success":
                node.classList.toggle("bg-success");
                break;

            case "error":
                node.classList.toggle("bg-danger");
                node.classList.toggle("text-white");
                break;

            default:
                node.classList.toggle("bg-light");
                break
        }

        let header = document.createElement("div");
        header.className = "toast-header";
        header.innerHTML = '<strong class="mr-auto">Alert</strong><button type="button" class="ml-2 mb-1 btn-close" data-bs-dismiss="toast"></button>';

        let body = document.createElement("div");
        body.className = "toast-body";
        body.innerText = msg;

        node.appendChild(header);
        node.appendChild(body);

        let observer = new MutationObserver(function (mutations) {
            for (let mutation of mutations) {
                if (mutation.attributeName === "class" && node.className.includes("hide")) {
                    node.remove();
                    observer.disconnect();
                }
            }
        });

        observer.observe(node, { attributes: true });

        document.getElementById(TOAST_CONTAINER_ID).appendChild(node);

        let toast = new bootstrap.Toast(node);
        toast.show();
    }

    let galleryDropdownOpen = document.getElementById("galleryDropdownOpen");
    if (galleryDropdownOpen !== null) {
        fetchBackground("/api/galleries", addGalleries);
    }

    document.getElementById("searchform").addEventListener("submit", validate);
});
