const trailer = document.getElementById("trailer");

const animateTrailer = (e, interacting) => {
  const x = e.clientX - trailer.offsetWidth / 2,
        y = e.clientY - trailer.offsetHeight / 2;
  
  const keyframes = {
    transform: `translate(${x}px, ${y}px) scale(${interacting ? 2 : 1})`
  }
  
  trailer.animate(keyframes, { 
    duration: 800, 
    fill: "forwards" 
  });
}


window.onmousemove = e => {
  const interactable = e.target.closest(".interactable"),
        interacting = interactable !== null;
    
  animateTrailer(e, interacting);
  

}


window.addEventListener('scroll', function() {
  const hiddenNav = document.getElementById('hidden-nav');
  if (window.scrollY > 300) {
    hiddenNav.classList.add('nav-visible');
  } else {
    hiddenNav.classList.remove('nav-visible');
  }
});


function toggleresponsive() {
  const ham = document.querySelector('#nav-icon3')
  const nav = document.querySelector('.mobile-nav')
  ham.classList.toggle('open')
  const wrapper = document.querySelector('.hamburger-wrapper')
  wrapper.classList.toggle('wrapper-active')
  nav.classList.toggle('mobile-active')
}


  particlesJS('particles-js', {
    "particles": {
      "number": {
        "value": 75,
        "density": {
          "enable": true,
          "value_area": 1000
        }
      },
      "color": {
        "value": "#dadada"
      },
      "size": {
        "value": 3,
        "random": true
      },
      "line_linked": {
        "enable": false
      },
      "move": {
        "enable": true,
        "speed": 0.5,
        "direction": "none",
        "random": false,
        "out_mode": "out"
      }
    },
    "interactivity": {
      "detect_on": "canvas",
      "events": {
        "onhover": {
          "enable": true,
          "mode": "repulse"
        },
        "onclick": {
          "enable": true,
          "mode": "push"
        },
        "resize": true
      }
    },
    "retina_detect": true
  });
