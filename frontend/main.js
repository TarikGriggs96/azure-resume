Window.addEventListener('DOMContentLoaded', (event) =>{
    getVisistCount();
})

const functionApi = '';

const getVisistCount = () => {
    let count = 30;
    fetch(functionApi).then(response => {
        return response .json()
    }).then (response =>{
        console.log("Website called function API.");
        count = response.count;
        document.getElementById("counter").innerText = count;
    }).catch(function(error){
        console.log(error);
    });
    return count
}