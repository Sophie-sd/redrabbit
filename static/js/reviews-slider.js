(function() {
  const slider = document.getElementById('reviewsSlider');
  const prevBtn = document.querySelector('.reviews-slider-container .slider-prev-btn');
  const nextBtn = document.querySelector('.reviews-slider-container .slider-next-btn');
  
  if (!slider || !prevBtn || !nextBtn) return;
  
  const scrollAmount = 350;
  
  prevBtn.addEventListener('click', function() {
    slider.scrollBy({
      left: -scrollAmount,
      behavior: 'smooth'
    });
  });
  
  nextBtn.addEventListener('click', function() {
    slider.scrollBy({
      left: scrollAmount,
      behavior: 'smooth'
    });
  });
  
  // Управління видимістю кнопок
  function updateButtonsVisibility() {
    const isAtStart = slider.scrollLeft === 0;
    const isAtEnd = slider.scrollLeft + slider.clientWidth >= slider.scrollWidth - 1;
    
    prevBtn.style.opacity = isAtStart ? '0.3' : '1';
    prevBtn.style.cursor = isAtStart ? 'default' : 'pointer';
    
    nextBtn.style.opacity = isAtEnd ? '0.3' : '1';
    nextBtn.style.cursor = isAtEnd ? 'default' : 'pointer';
  }
  
  slider.addEventListener('scroll', updateButtonsVisibility);
  updateButtonsVisibility();
})();
