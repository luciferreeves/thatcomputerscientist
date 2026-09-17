document.addEventListener('DOMContentLoaded', function () {
    const collapsableHeaders = document.querySelectorAll('.collapsable-header');
    collapsableHeaders.forEach(header => {
        header.addEventListener('click', function () {
            // Toggle active class on header
            this.classList.toggle('active');

            // Toggle collapsed class on parent
            const collapsableParent = this.closest('.collapsable');
            if (collapsableParent) {
                collapsableParent.classList.toggle('collapsed');
            }
        });
    });
});
