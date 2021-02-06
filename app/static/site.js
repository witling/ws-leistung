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

        console.log(note)
    }

    function validate(event) {
        let len = document.getElementById("searchbar").value.trim().length
        if (len < MIN_SEARCH_LENGTH) {
            error();
            event.preventDefault();
        }
    }

    document.getElementById("searchform").addEventListener("submit", validate);
})