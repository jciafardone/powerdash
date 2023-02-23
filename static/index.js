'use strict';

document.querySelector('#TestBtn')
  .addEventListener('click', (evt) => {
    evt.preventDefault();

    window.open("/wave_login", "popup", "width=400,height=800");
  });