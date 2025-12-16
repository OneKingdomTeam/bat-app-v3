/**
 * Assessment sharing functionality
 * Generates shareable links and copies to clipboard
 */
document.addEventListener('DOMContentLoaded', function() {

    // Add click handlers to all share buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('share-assessment-btn') ||
            event.target.closest('.share-assessment-btn')) {

            const button = event.target.classList.contains('share-assessment-btn')
                ? event.target
                : event.target.closest('.share-assessment-btn');

            const assessmentId = button.getAttribute('data-assessment-id');

            if (!assessmentId) {
                console.error('No assessment ID found');
                return;
            }

            // Generate shareable URL
            const shareUrl = `${window.location.origin}/share/assessment/${assessmentId}`;

            // Copy to clipboard
            copyToClipboard(shareUrl, button);
        }
    });

    function copyToClipboard(text, button) {
        // Modern clipboard API
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                showCopySuccess(button);
            }).catch(err => {
                console.error('Failed to copy:', err);
                showCopyError(button);
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            document.body.appendChild(textArea);
            textArea.select();

            try {
                document.execCommand('copy');
                showCopySuccess(button);
            } catch (err) {
                console.error('Failed to copy:', err);
                showCopyError(button);
            }

            document.body.removeChild(textArea);
        }
    }

    function showCopySuccess(button) {
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.classList.remove('is-light');
        button.classList.add('is-success');

        // Reset button after 2 seconds
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('is-success');
            button.classList.add('is-light');
        }, 2000);
    }

    function showCopyError(button) {
        const originalText = button.textContent;
        button.textContent = 'Failed';
        button.classList.remove('is-light');
        button.classList.add('is-danger');

        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('is-danger');
            button.classList.add('is-light');
        }, 2000);
    }
});
