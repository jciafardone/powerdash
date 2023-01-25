'use strict';

document.querySelector('#date-filter > form > input[type="submit"]')
  .addEventListener('click', (evt) => {
    evt.preventDefault();

    const formInputs ={
        startDate: document.querySelector('#start-date').value,
        endDate: document.querySelector('#end-date').value,
    };

    fetch('/date', {
        method: 'POST',
        body: JSON.stringify(formInputs),
        headers:{
            'Content-Type': 'application/json',
        },
    })
        .then((response)=>response.json())
        .then((responseJson)=>{
            console.log(formInputs)
            document.querySelector('#date-header').innerHTML = `For ${responseJson.startDate} to ${responseJson.endDate}`;
        });
});


document.querySelector('#date-filter').addEventListener('click', dateFilter);