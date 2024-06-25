// static/js/navbar.js

document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.navbar a');
    const contentContainer = document.getElementById('content-container');

    buttons.forEach(button => {
        // "Listen" for and respond to a "click"
        button.addEventListener('click', function(e) 
        {
            e.preventDefault();
            const targetId = button.dataset.target;
            
            // When a Navbar item is clicked, fetch it's specific html file
            fetch(`/static/content/${targetId}.html`)
                .then(response => {
                    // If reponse failed, display error message
                    if (!response.ok) {
                        throw new Error('Error loading content for:', targetId);
                    }
                    return response.text();
                })
                .then(html => {
                    console.log(`Loaded content for ${targetId}:`, html);
                    contentContainer.innerHTML = html;

                    // Add active class to the loaded content's html so that the appropriate
                    //  CSS can apply and only render the specified content
                    const loadedContent = contentContainer.querySelector('.content');
                    if (loadedContent) {
                        loadedContent.classList.add('active');
                    }
                })
                // Display error if content didn't load correctly.
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