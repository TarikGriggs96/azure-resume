// Visitor counter for the resume site.
// Set functionApi to your Azure Function URL once the backend is deployed.
const functionApi = '';

const getVisitCount = () => {
    if (!functionApi) return;
    fetch(functionApi)
        .then(response => response.json())
        .then(response => {
            console.log("Website called function API.");
            const count = Number(response.count).toLocaleString();
            // The count shows in two places: the "Live" strip under the intro and the footer.
            document.querySelectorAll(".visitor-count").forEach(el => (el.textContent = count));
        })
        .catch(error => console.log(error));
};

window.addEventListener('DOMContentLoaded', getVisitCount);
