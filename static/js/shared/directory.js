class DirectoryViewer {
    constructor(element) {
        this.element = element;
        this.folders = element.querySelectorAll('.folder-item');
        this.selectedFolder = null;

        this.setupEventListeners();
    }

    setupEventListeners() {
        this.folders.forEach(folder => {
            folder.addEventListener('click', (e) => this.handleFolderClick(e, folder));
            folder.addEventListener('dblclick', (e) => this.handleFolderDoubleClick(e, folder));
        });

        // Clear selection when clicking empty space
        this.element.addEventListener('click', (e) => {
            if (e.target === this.element || e.target.classList.contains('directory-content')) {
                this.clearSelection();
            }
        });
    }

    handleFolderClick(e, folder) {
        e.preventDefault();
        e.stopPropagation();

        this.clearSelection();
        this.selectFolder(folder);
    }

    handleFolderDoubleClick(e, folder) {
        e.preventDefault();
        const path = folder.dataset.path;
        if (!path) return;
        window.location.href = path;
    }

    selectFolder(folder) {
        if (this.selectedFolder) {
            this.selectedFolder.classList.remove('selected');
        }
        folder.classList.add('selected');
        this.selectedFolder = folder;
    }

    clearSelection() {
        if (this.selectedFolder) {
            this.selectedFolder.classList.remove('selected');
            this.selectedFolder = null;
        }
    }
}

// Initialize the directory viewer
document.addEventListener('DOMContentLoaded', () => {
    const dirViewer = new DirectoryViewer(document.querySelector('.directory-viewer'));
});