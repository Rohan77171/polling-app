// Make sure these functions are available globally
async function vote(pollId, optionId) {
    try {
        const response = await fetch('/vote/' + pollId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ option_id: optionId })
        });

        const data = await response.json();

        if (data.success) {
            // Update the vote count immediately
            const voteCountElement = document.getElementById('votes-' + optionId);
            if (voteCountElement) {
                voteCountElement.textContent = data.new_votes;
            }
            
            // Refresh the chart
            refreshResults(pollId);
            
            // Disable all vote buttons after voting
            document.querySelectorAll('.btn-vote').forEach(btn => {
                btn.disabled = true;
                btn.className = 'btn-voted';
                btn.textContent = 'Voted';
            });
            
            // Show success message
            showFlashMessage('Vote recorded successfully!', 'success');
        } else {
            showFlashMessage('Error: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showFlashMessage('Error submitting vote', 'error');
    }
}

async function refreshResults(pollId) {
    try {
        const response = await fetch('/results/' + pollId);
        const data = await response.json();
        
        updateChart(data.results);
        
        // Update UI based on voting status
        if (data.has_voted || !data.is_active) {
            document.querySelectorAll('.btn-vote').forEach(btn => {
                btn.disabled = true;
                btn.className = 'btn-voted';
                btn.textContent = 'Voted';
            });
        }
        
    } catch (error) {
        console.error('Error fetching results:', error);
    }
}

function updateChart(results) {
    const chartContainer = document.getElementById('resultsChart');
    const totalVotes = results.reduce((sum, option) => sum + option.votes, 0);
    
    let chartHTML = '';
    
    results.forEach(option => {
        const percentage = totalVotes > 0 ? (option.votes / totalVotes) * 100 : 0;
        
        chartHTML += '<div class="bar-container">' +
            '<div class="bar-label">' +
                '<span>' + option.text + '</span>' +
                '<span>' + option.votes + ' votes (' + percentage.toFixed(1) + '%)</span>' +
            '</div>' +
            '<div class="bar" style="width: ' + percentage + '%"></div>' +
        '</div>';
    });
    
    if (chartContainer) {
        chartContainer.innerHTML = chartHTML;
    }
}

function showFlashMessage(message, type) {
    // Create flash message element
    const flashDiv = document.createElement('div');
    flashDiv.className = 'alert alert-' + type;
    flashDiv.textContent = message;
    
    // Insert after navbar
    const container = document.querySelector('.container');
    if (container && container.firstChild) {
        container.insertBefore(flashDiv, container.firstChild);
    }
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (flashDiv.parentNode) {
            flashDiv.parentNode.removeChild(flashDiv);
        }
    }, 5000);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    const pollContainer = document.querySelector('.poll-container');
    if (pollContainer) {
        const pathParts = window.location.pathname.split('/');
        const pollId = pathParts[pathParts.length - 1];
        if (pollId && !isNaN(pollId)) {
            refreshResults(parseInt(pollId));
        }
    }
});