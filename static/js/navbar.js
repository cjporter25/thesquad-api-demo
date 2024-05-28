// static/js/navbar.js

document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.navbar a');
    const contentContainer = document.getElementById('content-container');

    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = button.dataset.target;

            fetch(`/static/content/${targetId}.html`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(html => {
                    console.log(`Loaded content for ${targetId}:`, html);
                    contentContainer.innerHTML = html;

                    // Add active class to the loaded content
                    const loadedContent = contentContainer.querySelector('.content');
                    if (loadedContent) {
                        loadedContent.classList.add('active');
                    }
                })
                .catch(error => {
                    console.error('Error loading content:', error);
                    contentContainer.innerHTML = '<p>Failed to load content.</p>';
                });

            // Remove active class from all buttons and content sections
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });

    // Activate the first section by default
    document.getElementById('squad-button').click();
});